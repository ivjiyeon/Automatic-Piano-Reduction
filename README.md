# Automatic Piano Reduction

Final-year project: an AI system that converts an orchestral score into a piano reduction — a version of the piece that a single pianist can play. The problem is framed as **note selection**: given a full score and a human-made piano reduction of it, the model learns, note by note, which notes survive into the reduction — then applies that judgment to reduce new scores.

The training example is Mozart's *Così fan tutte*: the full score and its reference piano reduction are parsed and aligned, so every note in the original is labelled `1` (kept in the reduction) or `0` (dropped).

## How it works

1. **Parsing & alignment** — `data.py` / `tools.py` load MusicXML scores with [music21](https://web.mit.edu/music21/) (`converter.parse`), transpose instruments to concert pitch, and flatten measures and voices into a per-note DataFrame (measure, offset, part, pitch, MIDI pitch, duration, tie, …). `merge_df()` aligns the original score with the reference reduction to produce the per-note `chosen` label. Parsed DataFrames are cached as `.pkl` files in `df/`.
2. **Musical features** — `features.py` computes 17 features per note based on the definitions in the project report: `bass_line`, `highest` / `lowest`, `in_chord`, `harmony`, `strong_beats`, `onset_after_rest`, `entrance_effect`, `pitch_distance`, `vertical_doubling`, `rhythm_variety`, `sustained_rhythm`, and more.
3. **Models** —
   - Classical baselines in `data.py` (scikit-learn): KNN, linear SVM, decision tree, random forest, and Gaussian naive Bayes, evaluated with accuracy, macro-F1, precision, and recall on stratified train/test/validation splits.
   - Neural models in `keras_models.py` (Keras/TensorFlow): dense, LSTM, GRU, and bidirectional GRU architectures, each in plain and feature-augmented variants. They take a 128-dim pitch-class vector per time step and output a 128-dim sigmoid vector of note-selection probabilities per pitch class.

## Project structure

| Path | Contents |
| --- | --- |
| `data.py` | Main pipeline: score loading, alignment/labelling, feature matrix, baseline training and evaluation (Spyder/Jupyter cell-style script) |
| `features.py` | The 17 musical feature functions (DataFrame in → feature column out) |
| `keras_models.py` | Keras model factories: dense / LSTM / GRU / BiGRU, with and without extra features |
| `tools.py` | Data-loading and feature utilities (earlier/parallel module) |
| `cosi/` | MusicXML data for *Così fan tutte* (full score + reference reduction) |
| `df/` | Cached parsed DataFrames (`.pkl`) |
| `1702/`, `1802/` | Two versions of the piano-reduction codebase the project builds on, including notebooks |

## Running it

The main script is written in notebook-cell style (`# %%` markers):

```bash
pip install music21 pandas numpy scikit-learn tensorflow
python data.py
```

Run the cells sequentially in Spyder or Jupyter, or execute the script directly: it loads (or parses and caches) the score DataFrames, builds the labelled feature matrix, then trains and evaluates the baseline models, printing their metrics. The Keras models in `keras_models.py` are factory functions — call one to get a compiled model, then train it on the DataFrame-derived sequences.

## Context

Built as a B.Sc. Computer Science final-year project at The Chinese University of Hong Kong. The interesting difficulty is that "which notes matter" is a musical judgment — harmony, bass line, rhythm, and entrances — so most of the work is in features that capture that judgment well enough for a model to learn it.
