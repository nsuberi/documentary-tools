import os
import json

def extract_transcript_text(json_folder="transcripts", output_folder="txtfiles"):
    """
    Reads all JSON files in 'json_folder', extracts the combined transcript text,
    and saves it into .txt files.
    """
    
    # Make sure the folder exists
    if not os.path.isdir(json_folder):
        print(f"Directory '{json_folder}' does not exist.")
        return

    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            json_path = os.path.join(json_folder, filename)
            
            # Load the JSON data
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract the transcripts list:
            # data["results"]["transcripts"] should be a list of dicts,
            # each with a "transcript" key
            transcripts_list = data.get("results", {}).get("transcripts", [])
            
            # Combine all transcript text into a single string
            combined_transcript = "\n".join(
                t.get("transcript", "") for t in transcripts_list
            )

            # Build the new output filename:
            # e.g., "transcription_CasaRetablo-001_06102354739509227.json"
            # -> "transcription_CasaRetablo-001.txt"
            base_name = os.path.splitext(filename)[0]  # remove .json
            # Split at underscores, keep only the first two parts, then add .txt
            # (Assumes a naming convention like "transcription_<something>_<numbers>.json")
            parts = base_name.split("_")
            if len(parts) > 2:
                # Reconstruct everything up to the second underscore
                output_filename = "_".join(parts[:2]) + ".txt"
            else:
                # If there's only one underscore or fewer, just replace extension with .txt
                output_filename = base_name + ".txt"
            
            output_path = os.path.join(output_folder, output_filename)
            
            # Write the combined transcript to a .txt file
            with open(output_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(combined_transcript)
            
            print(f"Wrote transcript text to: {output_path}")

if __name__ == "__main__":
    extract_transcript_text("transcripts", "txtfiles")
