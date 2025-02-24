import os
import json
from pathlib import Path

def copy_o1_transcriptions(results_dir="résultats", reference_dir="transcriptions_de_référence"):
    """
    Iterate through JSON files in results_dir, find OpenAI/o1 model results,
    and copy their transcriptions to reference_dir with .md extension
    """
    # Create reference directory if it doesn't exist
    Path(reference_dir).mkdir(parents=True, exist_ok=True)
    
    # Counter for tracking processed files
    copied_count = 0
    
    # Iterate through all files in results directory
    for filename in os.listdir(results_dir):
        if not filename.endswith('.json'):
            continue
            
        result_file_path = os.path.join(results_dir, filename)
        
        # Read and parse JSON file
        try:
            with open(result_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check if this is an OpenAI/o1 model result
            if (
                "model_info" in data 
                and "id" in data["model_info"] 
                and data["model_info"]["id"] == "openai/o1"
            ):
                # Get the transcription result
                transcription = data.get("result", "")
                
                # Create corresponding .md filename
                md_filename = os.path.splitext(filename)[0] + ".md"
                md_file_path = os.path.join(reference_dir, md_filename)
                
                # Write transcription to .md file
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                    
                copied_count += 1
                print(f"Copied transcription to: {md_file_path}")
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error processing {filename}: {str(e)}")
    
    print(f"\nProcessing complete. Copied {copied_count} transcription(s) to {reference_dir}")

if __name__ == "__main__":
    copy_o1_transcriptions() 