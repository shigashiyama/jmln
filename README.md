# JMLN: Japanese Multi-Domain Lexical Normalization Dataset

## Requirements

- Python 3.10 or later
- The Python packages listed in `requirements.txt`
- Access to the original datasets:
    - BCCWJ 1.1 <https://clrd.ninjal.ac.jp/bccwj/en/index.html>
    - Hot Pepper Beauty data in the Recruit Dataset <https://www.doi.org/10.32130/idr.4.1>
    - Rakuten Dataset <https://www.doi.org/10.32130/idr.2.0>
    - Nicovideo Comment etc. data <https://www.doi.org/10.32130/idr.3.1>
    - Nicopedia data <https://www.doi.org/10.32130/idr.3.2>
    - Nagoya University Conversation Corpus <https://mmsrv.ninjal.ac.jp/nucc/en/index.html>
    - Japanese and Chinese Skype Conversation Corpus <http://nakamata.info/database/>

## How to Restore the Data

The files in `data/mask` contain annotation information only.

The following commands extract the original text and merge it with the annotation information to restore the complete TSV files. Before running these commands, make sure to create symbolic links to the original dataset directories as specified in `bin/restore_*.sh`.
~~~~
./bin/restore_01-02_bccwj.sh
./bin/restore_03-04_recruite.sh
./bin/restore_05_rakuten_ichiba.sh
./bin/restore_06_rakuten_travel.sh
./bin/restore_07_rakuten_recipe.sh
./bin/restore_09_niconico_video.sh
./bin/restore_10_niconico_pedia.sh
./bin/restore_13_nucc.sh
./bin/restore_14_skype.sh
~~~~

The following command converts the TSV files into JSON format.
~~~~
python src/tsv_to_json.py -i data/tsv/word_level -n data/normid/normids_20250326.txt -s data/id_data_split -o data/json
~~~~

## Main Files

- `data/normid/normids_20250326.txt`: Mapping of standard form IDs
- `data/tsv/word_level/*.txt`: Word-level TSV files (raw text + annotation information; one word per line)
- `data/tsv/sent_level/*.txt`: Sentence-level TSV files (raw text only; one sentence per line)
- `data/json/*.json`: JSON files (raw text + annotation information)

## Word-level TSV Format

- Column 1: Surface form
- Column 2: Part-of-speech tag
- Column 3: Conjugation type
- Column 4: Conjugation form
- Column 5: Word category (see [1])
- Column 6: Standard form ID (SForm ID or `norm_id`; see [1])

Lines beginning with `#` indicate sentence IDs, and blank lines mark sentence boundaries.
The standard forms corresponding to each SForm ID are listed in `normids_20250326.txt`.

## JSON Format

Most attributes are the same as those in the word-level TSV files, but the standard-form information is integrated into the `norm_forms` field. In addition, the sentences are split into train/dev/test sets.

## Data Sources

- 01_BJ-OC : BCCWJ-OC (Yahoo! Chiebukuro)
- 02_BJ-OY : BCCWJ-OY (Yahoo! Blog)
- 03_RC-BLG: Recruit Dataset (Hot Pepper Beauty data, shop blogs)
- 04_RC-REV: Recruit Dataset (Hot Pepper Beauty data, reviews)
- 05_RK-ICB: Rakuten Dataset (Rakuten Ichiba, product and shop reviews)
- 06_RK-TRV: Rakuten Dataset (Rakuten Travel, reviews)
- 07_RK-RCP: Rakuten Dataset (Rakuten Recipe)
- 08_AM    : Multilingual Amazon Review Corpus; The data derived from this source is not included in this dataset.
- 09_NC-VID: Nicovideo Comment etc. data (Movie titles and comments)
- 10_NC-PED: Nicopedia data
- 12_JW    : Japanese Wikipedia Typo Dataset
- 13_NU    : Nagoya University Conversation Corpus
- 14_SK    : Japanese and Chinese Skype Conversation Corpus

## License

The following files are derived from the Japanese Wikipedia Typo Dataset and have been modified for this dataset. Changes include reformatting, annotation, and conversion into our release formats. These files are licensed under CC BY-SA 3.0. See `LICENSE-CC-BY-SA-3.0` for details.

- `data/json/12_JW.json`
- `data/tsv/sent_level/12_JW-ctrl.txt`
- `data/tsv/word_level/12_JW-ctrl.txt`

All other files are released under the MIT License. See `LICENSE`.

## Citation

Please cite the following paper [1].
~~~~
@inproceedings{higashiyama-utiyama-2025-comprehensive,
    title = "Comprehensive Evaluation on Lexical Normalization: Boundary-Aware Approaches for Unsegmented Languages",
    author = "Higashiyama, Shohei  and
      Utiyama, Masao",
    editor = "Christodoulopoulos, Christos  and
      Chakraborty, Tanmoy  and
      Rose, Carolyn  and
      Peng, Violet",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2025",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.findings-emnlp.684/",
    doi = "10.18653/v1/2025.findings-emnlp.684",
    pages = "12774--12799",
    ISBN = "979-8-89176-335-7",
    abstract = "Lexical normalization research has sought to tackle the challenge of processing informal expressions in user-generated text, yet the absence of comprehensive evaluations leaves it unclear which methods excel across multiple perspectives. Focusing on unsegmented languages, we make three key contributions: (1) creating a large-scale, multi-domain Japanese normalization dataset, (2) developing normalization methods based on state-of-the-art pre-trained models, and (3) conducting experiments across multiple evaluation perspectives. Our experiments show that both encoder-only and decoder-only approaches achieve promising results in both accuracy and efficiency."
}
~~~~

## Acknowledgements
The annotation data was created by [IR-Advanced Linguistic Technologies Inc](https://ir-alt.co.jp/).

## Contact

Shohei Higashiyama
