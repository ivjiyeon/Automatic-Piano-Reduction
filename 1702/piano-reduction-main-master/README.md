# Piano Reduction 2017

2017 - 2018 FYP by Isaac Yiu & Jason Choi

## Tips

1.  Use Python 3! It's a crime to still use python 2 in current year. ¯\\_(ツ)_
2.  The musical scores (for training and testing models) can be found in the `sample` folder.
3.  The utility in folder `scoreboard` provides a visualization of machine learning feature and models. Refer to the `README.md` in that folder.
4.  There are unit tests that can be used to verify the correctness of each machine learning feature, use `pytest`.
5.  The machine learning model code can be found at `learning/models`.

## Setup

1.  (Recommended but not required) Use a virtualenv:

    ```sh
    python3 -m venv venv

    # Every time before working on the shell:
    source venv/bin/activate
    ```

2.  Install dependencies:

    ```sh
    pip3 install -r requirements.txt

    # To install dev dependencies:
    pip3 install -r requirements-dev.txt
    ```

3.  Run `python3 learning/test.py` for usage. If you would like to execute the post-processor independently, you can run `python3 postprocessor/run.py`.

## Development

-   Linting:

    ```sh
    flake8
    ```

-   Unit testing:

    ```sh
    pytest
    ```

## Command line interface

To access to command line, use:

```sh
python3 -m learning <args...>

# For help
python3 -m learning --help
python3 -m learning <command> --help

# Train model only
# This defaults to saving the model to "trained/<model name>.model".
python3 -m learning.models.<model name> train

# Reduce from trained model
# This defaults to loading from the above file.
python3 -m learning.models.<model name> reduce [-o <output file>] <input file>[:<reduced file>]

python3 -m learning reduce -m <model file> [-o <output file>] <input file>[:<reduced file>]

# Inspect sample pair
python3 -m learning inspect <original file>:<reduced file>
```
