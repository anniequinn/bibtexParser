# bibtexParser

## What does it do?
The BibtexParser is a Python class designed to read, parse, and extract metadata from BibTeX files. It turns BibTeX entries into a structured JSON format, making it easier to manipulate and access bibliographic data. The parser can also resolve Digital Object Identifiers (DOIs) to the redirected URLs, facilitating further metadata enrichment by parsing article HTML pages.

## How do I use it?

### Running from the Shell
To use `BibtexParser`, you can run the script directly from the command line. Navigate to the directory containing the script and execute it by specifying the path to your `.bib` file. If you want to save the output as a JSON file in the same directory as the script, use the `--save` flag.

*Example:*
```shell
python bibtex_parser.py /path/to/your/file.bib --save
```

This will parse the specified `.bib` file and save the parsed entries as `parsed_bibtex.json` in the script's directory. If the `--save` flag is omitted, the output will be printed to the console.

-----

### Import to script
You can also import and use the `BibtexParser` class in your own Python scripts. First, ensure that the `bibtex_parser.py` file is accessible in your project's directory structure or Python path.

*Example:*
```python
from bibtexParser import bibtexParser

file_path = '/path/to/your/file.bib'

# Initialize the parser with your BibTeX file path
parser = bibtexParser(file_path)

# Parse the BibTeX file
parsed_data = parser.parse_bibtex()

# Access the parsed data
print(parsed_data)
```
