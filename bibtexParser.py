import os
import logging
import re
import requests
import json

# Set up a logging to print out
logging.basicConfig(
    level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s"
)


class bibtexParser:
    def __init__(self, file_path):
        """Initialise bibtexParser with a file path to a .bib file."""
        self.file_path = file_path

        # Precompile the regular expression to split bibtex string into chunks
        self.pattern_chunk_split = re.compile(r"(@[A-Za-z]+{)")

        self.bibtex_string = None
        self.metadata_entries = []
        self.parsed_entries = []

    def read_bibtex_file(self):
        """Read the .bib file and store the contents as a string."""
        logging.info(f"Reading {self.file_path}")
        if not self.file_path.endswith(".bib"):
            logging.error(
                f"Invalid file type: {self.file_path}, must be a .bib file"
            )
            return  # Abort the operation after logging the error

        if not os.path.exists(self.file_path):
            logging.error(f"File not found: {self.file_path}")
            return  # Abort the operation after logging the error

        try:
            with open(self.file_path, "r") as f:
                self.bibtex_string = f.read()

            if self.bibtex_string:
                logging.info(f"Successfully read {self.file_path}")
            else:
                logging.warning(f"The file {self.file_path} is empty")
        except Exception as e:
            logging.error(f"Error reading {self.file_path}: {str(e)}")

    def extract_metadata(self):
        """
        Splits the BibTeX string into chunks and extracts metadata for each
        entry.

        Chunks are split using '@entry' as a delimiter. The method then filters
        out blank  entries and delimiters, retaining only chunks with metadata.
        The metadata is stored as a string in a list.
        """
        logging.info("Extracting metadata")
        try:
            chunks = re.split(
                self.pattern_chunk_split, self.bibtex_string.strip()
            )

            for chunk in chunks:
                metadata = self._extract_entry_metadata(chunk)
                if metadata:
                    self.metadata_entries.append(metadata)
                else:
                    logging.debug(f"Skipping invalid metadata: {chunk[:30]}")

            logging.info(
                f"{len(self.metadata_entries)} entry metadata extracted"
            )

        except re.error as e:
            # If the pattern to split the string into chunks is invalid
            logging.error(f"Invalid regular expression pattern: {str(e)}")

    def parse_metadata(self, pattern=None):
        """
        Parse each metadata string into a dictionary of key-value pairs, where
        each dictionary represents a single bibtex entry.
        """
        logging.info("Parsing the bibtex entries")
        if not pattern:
            pattern = r'(\w+)\s*=\s*(?:"([^"]*)"|\{([^\}]*)\}|(\w+))'

        for metadata in self.metadata_entries:
            parsed_data = self._parse_metadata(metadata, pattern)
            self.parsed_entries.append(parsed_data)

            if not parsed_data:
                logging.debug(f"Failed to parse: {metadata[:30]}")

        logging.info(f"{len(self.parsed_entries)} valid entries parsed")

    def add_urls_from_doi(self):
        """
        If the 'doi' key is present, construct the URL with the DOI. Update the
        entry with the redirected URL.
        """
        logging.info("Adding redirected URLs from DOI")
        for idx, entry in enumerate(self.parsed_entries):
            if "doi" in entry:
                url = self._get_url_from_doi(entry["doi"], idx=idx)
                self.parsed_entries[idx]["doi_url"] = url
                self.parsed_entries[idx]["url"] = url
            else:
                logging.info(f"No DOI found in entry {idx}")
        logging.info("Adding redirected URLs completed")

    def extract_parsed_entries(self):
        """Return the parsed entries as a list of dictionaries."""
        logging.info(
            f"{len(self.parsed_entries)} entries extracted from {self.file_path}"  # noqa
        )
        return json.dumps(self.parsed_entries, indent=4)

    def parse_bibtex(self, json=False):
        """
        Main entry point to parse the bibtex file. Read the bibtex string,
        chunk the bibtex string, parse the entries, add URLs from DOI, and
        return the parsed entries as a JSON or a list of dictionaries.
        """
        try:
            self.read_bibtex_file()
            self.extract_metadata()
            self.parse_metadata()
            self.add_urls_from_doi()

            if json:
                self.extract_parsed_entries()
            else:
                return self.parsed_entries

        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")

    def save_parsed_entries(self, output_path):
        """Save the parsed entries to a json."""
        with open(output_path, "w") as f:
            json_data = self.extract_parsed_entries()
            f.write(json_data)
        logging.info(f"Saved parsed entries to {output_path}")

    def _extract_entry_metadata(self, chunk):
        """
        Extracts the metadata from a chunk if it is valid. An invalid chunk is
        one that is empty or contains the delimiter '@'.

        Parameters:
        - chunk (str): A chunk of the BibTeX string.

        Returns:
        - str: The metadata if valid, None otherwise.
        """
        chunk = chunk.strip()
        if chunk and chunk[0] != "@":
            return chunk

    def _parse_metadata(self, metadata, pattern):
        """
        Parses the metadata string for a single entry into a dictionary of
        key-value pairs.

        This method uses regular expressions to extract bibtex entry fields
        and their values from the metadata.

        It handles exceptions related to regular expression errors.

        Parameters:
        - metadata (str): The metadata string to parse.
        - pattern (str): The regular expression pattern used to identify
          key-value pairs within the metadata.

        Returns:
        - dict: A dictionary containing parsed key-value pairs from the bibtex
          entry, or None if an error occurs.
        """
        try:
            matches = re.findall(pattern, metadata)
            matches = [
                tuple(x for x in match if x not in (None, ""))
                for match in matches
            ]
            parsed_data = {key.lower(): value for key, value in matches}
            return parsed_data

        except re.error as e:
            logging.error(f"Invalid regular expression pattern: {str(e)}")
            return None

    def _get_url_from_doi(self, doi, idx=None):
        """
        Constructs a URL from a DOI and retrieves the final redirected URL.

        This method attempts to construct a URL using the extracted. It then
        uses an HTTP HEAD request to follow redirects and retrieve the final
        redirected URL.

        It handles various HTTP and request-related exceptions.

        Parameters:
        - doi (str): The Digital Object Identifier (DOI) from which to
          construct the URL.
        - idx (int, optional): The index of the entry, used for logging.

        Returns:
        - str: The final redirected URL obtained from the DOI, or None if an
        error occurs.
        """
        try:
            url = "http://dx.doi.org/" + doi
            response = requests.head(url, allow_redirects=True)
            return response.url

        except requests.exceptions.RequestException as e:
            logging.error(
                f"An error occurred while getting URL for entry {idx}, DOI {doi}: {str(e)}"  # noqa
            )
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while getting URL for entry {idx}, DOI {doi}: {str(e)}"  # noqa
            )
        return None


def main():
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Parse a BibTeX file and optionally save the output to script directory."  # noqa
    )
    parser.add_argument(
        "file_path", type=str, help="The file path to the .bib file."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="""
        Whether to save the output to script directory. If flag is set, the
        output will be saved. If flag is ommitted, the output will be printed
        to the console.
        """
    )

    args = parser.parse_args()

    parser = bibtexParser(args.file_path)
    parser.parse_bibtex(json=True)

    if args.save:
        file_directory = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(file_directory, "parsed_bibtex.json")
        parser.save_parsed_entries(output_file_path)
    else:
        print(parser.extract_parsed_entries())


if __name__ == "__main__":
    main()
