# bibtexParser

## What does it do?
Gathering academic references usually means grappling with inconsistent formats or excessive copying and pasting, a real headache if you're looking to use this information in coding projects. 

Enter `bibtexParser`: a Python class designed to convert BibTeX files into a structured JSON. It takes your `.bib` file, breaks it down into individual entries, and extracts metadata such as title, author, and publication. 

DOIs are great because they avoid broken links by redirecting to the actual articles. But this thing that makes them great is a pain for coding because you can't scrape or parse that DOI link. `bibtexParser` solves this by retrieving the redirected URLs from DOIs, enabling you to further enrich your metadata.

## How do I use it?

### 1. Running from the Shell
To use `BibtexParser`, you can run the script directly from the command line. Navigate to the directory containing the script and execute it by specifying the path to your `.bib` file. 

If you want to save the output, add the `--save` flag and the parsed entries will be saved as `parsed_bibtex.json` in the same directory as the script. If the `--save` flag is omitted, the output will be pretty printed to the console.

```shell
# Shell example
python bibtex_parser.py /path/to/your/file.bib --save
```

### 2. Import to script
You can also import and use the `BibtexParser` class in your own Python scripts.

```python
# Python script example
from bibtexParser import bibtexParser

file_path = '/path/to/your/file.bib'

# Initialize the parser with your BibTeX file path
parser = bibtexParser(file_path)

# Parse the BibTeX file
parsed_data = parser.parse_bibtex()

# Access the parsed data
print(parsed_data)
```
