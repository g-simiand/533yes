import os
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import concurrent.futures
from functools import partial
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the directories (these mirror those used in benchmark_htr.ipynb / utils.py)
results_dir = Path("./résultats")
images_dir = Path("./images")
kraken_models_dir = Path("./kraken_models")

# Create directories if they do not exist
results_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)
kraken_models_dir.mkdir(exist_ok=True)

def process_image_kraken(img_path, kraken_model):
    """
    Process an image with a Kraken model using the Kraken CLI.
    
    This function builds a command of the form:
      kraken ocr -i <input_image> <tmp_output_file> --model <kraken_model>
    Note the correct ordering of the input pair immediately after the -i flag.
    
    Args:
        img_path (Path): Path to the image file.
        kraken_model (Path): Path to the Kraken model file.
    
    Returns:
        dict: A dictionary containing the result data in a format compatible with
              our main logic.
    """
    safe_model_name = kraken_model.stem.replace(" ", "_")
    result_file = results_dir / f"{img_path.stem}_{safe_model_name}.json"
    
    # Skip processing if the result file already exists
    if result_file.exists():
        print(f"Skipping existing result: {result_file}")
        return None
    
    # Temporary file to hold Kraken's OCR output
    tmp_output_file = results_dir / f"{img_path.stem}_{safe_model_name}_temp.txt"
    
    # Build the command with proper input file pair syntax:
    # Instead of using a separate "-o" option, we provide:
    # "-i <input_image> <tmp_output_file>"
    command = [
        "kraken",
        "-v",
        "-i", str(img_path), str(tmp_output_file),
        "segment",
        "-bl",
        "ocr",
        "--model", str(kraken_model)
    ]
    
    start_time = time.time()
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"STDOUT for {img_path.name}:", result.stdout)
        print(f"STDERR for {img_path.name}:", result.stderr)
        if result.returncode != 0:
            print(f"Command failed with return code {result.returncode}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error processing {img_path.name} with {kraken_model.name}: {e.stderr.strip()}")
        return None
    latency = time.time() - start_time
    
    # Read the OCR output from the temporary file
    try:
        with open(tmp_output_file, "r", encoding="utf-8") as f:
            transcription = f.read().strip()
        # Delete the temporary file after reading its content
        tmp_output_file.unlink()
    except Exception as e:
        print(f"Error reading temporary output for {img_path.name} with {kraken_model.name}: {str(e)}")
        transcription = ""
    
    # Build the result data dictionary (compatible with our main logic)
    result_data = {
        "model": safe_model_name,
        "editeur": "kraken",
        "modele_type": "libre",
        "image": str(img_path),
        "result": transcription,
        "timestamp": datetime.now().isoformat(),
        "model_info": {"path": str(kraken_model)},
        "usage": {},
        "latency": latency
    }
    
    # Save the result to a JSON file in the results directory
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {img_path.name} with {kraken_model.name}")
    return result_data

def main():
    # Gather image files (supporting jpg, jpeg, png)
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png"))
    if not image_files:
        print("No images found in the 'images' directory.")
        return
    
    # Gather Kraken model files (expecting .pt files; adjust pattern if needed)
    kraken_model_files = list(kraken_models_dir.glob("*.pt")) + list(kraken_models_dir.glob("*.mlmodel"))
    if not kraken_model_files:
        print("No Kraken models found in the 'kraken_models' directory.")
        return
    
    results = []
    max_workers = 4  # You can adjust the number of worker threads as needed
    
    # Iterate over each Kraken model
    for kraken_model in kraken_model_files:
        print(f"\nProcessing images with model: {kraken_model.name}")
        # Use functools.partial to fix the kraken_model parameter for the worker function
        process_fn = partial(process_image_kraken, kraken_model=kraken_model)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_img = {executor.submit(process_fn, img_path): img_path for img_path in image_files}
            for future in tqdm(
                concurrent.futures.as_completed(future_to_img),
                total=len(future_to_img),
                desc=f"Images for {kraken_model.name}",
                leave=False
            ):
                result = future.result()
                if result is not None:
                    results.append(result)
    
    print(f"\nCompleted processing. Total results: {len(results)}")
    
if __name__ == "__main__":
    main() 