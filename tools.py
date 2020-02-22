# %%
import music21
import copy
from os import listdir, path, mkdir
from collections import OrderedDict, defaultdict
import pandas as pd
import numpy as np


def load_df(folder, num, use_cache=True):
    """Return the dataframes of the specified musicXML file

    Keyword arguments:
    folder, num -- the num-th file of the folder is returned
    use_cache -- whether the cached version should be used.
                        If not, a new one will be generated
    """
    files = sorted([f for f in listdir(folder) if f[0] != '.'])
    try:
        filename = folder + '/' + files[num]
    except:
        raise Exception(':O(')
    if not path.exists('df'):
        mkdir('df')
    if not path.exists('df/' + folder):
        mkdir('df/' + folder)
    if path.isfile('df/' + filename + '.0.pkl') and use_cache:
        res = []
        for i in range(3):
            res.append(pd.read_pickle('df/' + filename + ('.%d.pkl' % i)))
    else:
        print('Creating df/' + filename)
        res = score_to_df(music21.converter.parse(filename))
        for i in range(len(res)):
            res[i].to_pickle('df/' + filename + ('.%d.pkl' % i))
    return res


def load_cosi(num, use_cache=True):
    """Return the dataframes of the specified cosi musicXML file, combined with the original score of it

    Keyword arguments:
    num -- the num-th file of the Cosi fan tutte in the folder "cosi" are used
    use_cache -- whether the cached version should be used.
                        If not, a new one will be generated
    """
    x_res = load_df('cosi', 0, use_cache)
    y_res = load_df('cosi', num, use_cache)
    if not path.exists('df'):
        mkdir('df')
    if not path.exists('df/merged_cosi'):
        mkdir('df/merged_cosi')
    if path.isfile('df/merged_cosi/%d.pkl' % num) and use_cache:
        return [pd.read_pickle('df/merged_cosi/%d.pkl' % num)] + x_res[1:]
    else:
        print('Creating df/merged_cosi/%d.pkl' % num)
        res = merge_df(x_res[0], y_res[0])
        res.to_pickle('df/merged_cosi/%d.pkl' % num)
        return [res] + x_res[1:]


def score_to_df(original_score_0):
    """Convert the music21 object into dataframes
        *** The ties are broken now but they are not used currently ***
    """
    original_score_1 = copy.deepcopy(original_score_0)
    for part in original_score_1.parts:
        transpose = 0
        try:
            transpose = part.getInstrument().transposition.semitones
        except:
            transpose = 0
        #print(part.getInstrument(), transpose)
        try:
            for measure in part.getElementsByClass(music21.stream.Measure):
                for element in measure.notesAndRests:
                    # print(element)
                    if type(element) is music21.note.Note:
                        element.pitch.ps += transpose
                    elif type(element) is music21.chord.Chord:
                        for note in element._notes:
                            note.pitch.ps += transpose
                    #print('NOW ', element)
                for voice in measure.getElementsByClass(music21.stream.Voice):
                    # print(voice)
                    for element in voice.notesAndRests:
                        # print(element)
                        if type(element) is music21.note.Note:
                            element.pitch.ps += transpose
                        elif type(element) is music21.chord.Chord:
                            for note in element._notes:
                                note.pitch.ps += transpose
                        #print('NOW ', element)
        except:
            print("WHY")
    original_score = original_score_1.voicesToParts()
    score = music21.stream.Score()
    for element in original_score._elements:
        if type(element) is music21.text.TextBox or type(element) is music21.metadata.Metadata:
            score.insert(0, element)
    parts = {'L': music21.stream.Part(), 'R': music21.stream.Part()}
    parts['L'].insert(0, music21.instrument.fromString('Piano'))
    parts['R'].insert(0, music21.instrument.fromString('Piano'))
    hands = [0, 1]
    notes = pd.DataFrame(columns=[
                         'measure', 'offset', 'part', 'pitch', 'ps', 'duration', 'tie', 'chosen', 'color'])
    others = pd.DataFrame(columns=['measure', 'offset', 'element'])
    bar_lengths = pd.Series()
    nc = 0
    oc = 0
    original_measures = original_score.measureOffsetMap()
    xx = []
    measure_elements = {}
    for offset, measures in original_measures.items():
        measure = music21.stream.Measure()
        for original_measure in measures:
            if original_measure.barDuration.quarterLength > 0:
                bar_length = original_measure.barDuration.quarterLength
        bar_lengths.loc[offset] = bar_length
        pc = 0
        for original_measure in measures:
            for element in original_measure.notesAndRests:
                if type(element) is music21.note.Note:
                    notes.loc[nc] = [offset, element.offset, pc, element.pitch,
                                     element.pitch.ps, element.duration, element.tie, 1, element.style.color]
                    nc += 1
                elif type(element) is music21.chord.Chord:
                    for note in element._notes:
                        notes.loc[nc] = [offset, element.offset, pc, note.pitch,
                                         note.pitch.ps, element.duration, note.tie, 1, note.style.color]
                        nc += 1
            for element in original_measure.getElementsByClass(music21.key.KeySignature):
                others.loc[oc] = [offset, element.offset, element]
                oc += 1
            for element in original_measure.getElementsByClass(music21.tempo.MetronomeMark):
                others.loc[oc] = [offset, element.offset, element]
                oc += 1
            for element in original_measure.getElementsByClass(music21.dynamics.Dynamic):
                others.loc[oc] = [offset, element.offset, element]
                oc += 1
            for element in original_measure.getElementsByClass(music21.expressions.TextExpression):
                others.loc[oc] = [offset, element.offset, element]
                oc += 1
            for element in original_measure.getElementsByClass(music21.meter.TimeSignature):
                others.loc[oc] = [offset, element.offset, element]
                oc += 1
            pc += 1
    notes = notes.sort_values(['measure', 'offset', 'ps']).drop_duplicates(
        ['measure', 'offset', 'ps'])
    return [notes, others, bar_lengths]


def merge_df(x, y):
    """Combine two dataframes into one
    """
    x = x.rename(columns={'chosen': 'x_train'})
    x['offset'] = x['offset'].astype('object')
    x['measure'] = x['measure'].astype('object')
    y = y.rename(columns={'chosen': 'y_train'})
    y['offset'] = y['offset'].astype('object')
    y['measure'] = y['measure'].astype('object')
    del y['tie'], y['color'], y['part']
    new_df = x.merge(y, how='outer', on=['measure', 'offset', 'ps'])
    new_df['x_train'] = new_df['x_train'].fillna(0)
    new_df['y_train'] = new_df['y_train'].fillna(0)
    new_df['part'] = new_df['part'].fillna(-1)
    new_df['duration'] = pd.Series()
    new_df['pitch'] = pd.Series()
    for ind in new_df.index:
        if pd.isnull(new_df.at[ind, 'duration_x']):
            new_df.at[ind, 'duration'] = new_df.at[ind, 'duration_y']
        else:
            new_df.at[ind, 'duration'] = new_df.at[ind, 'duration_x']
    for ind in new_df.index:
        if pd.isnull(new_df.at[ind, 'pitch_x']):
            new_df.at[ind, 'pitch'] = new_df.at[ind, 'pitch_y']
        else:
            new_df.at[ind, 'pitch'] = new_df.at[ind, 'pitch_x']
        if pd.isnull(new_df.at[ind, 'tie']):
            new_df.at[ind, 'tie'] = None
    del new_df['duration_x'], new_df['duration_y'], new_df['pitch_x'], new_df['pitch_y']
    new_df = new_df.sort_values(['measure', 'offset', 'ps'])
    return new_df

# FEATURES


def in_chord(df):
    return df['color'].apply(lambda x: (not pd.isnull(x) and x != '#000000')*1)


def lowest(df):
    s = pd.Series()
    ps = defaultdict(lambda: 999)
    for ind, row in df.iterrows():
        if row['x_train'] == 0:
            continue
        if row['ps'] < ps[(row['measure'], row['offset'])]:
            ps[(row['measure'], row['offset'])] = row['ps']
    for ind, row in df.iterrows():
        s.loc[ind] = (row['ps'] == ps[(row['measure'], row['offset'])]) * 1
    return s


def active_rhythm(df):
    counts = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        counts[row['measure'], row['part']] += 1
    most = defaultdict(lambda: 0)
    for measure, part in counts:
        if counts[measure, part] > most[measure] and part >= 0:
            most[measure] = counts[measure, part]
    s = pd.Series()
    for ind, row in df.iterrows():
        s.loc[ind] = (counts[row['measure'], row['part']]
                      == most[row['measure']]) * 1
    return s


def bass_line(df):
    notes = defaultdict(list)
    for ind, row in df.iterrows():
        notes[row['measure'], row['part']].append(row['ps'])
    lowest = defaultdict(lambda: 10000)
    for measure, part in notes:
        notes[measure, part] = np.median(notes[measure, part])
        if np.median(notes[measure, part]) < lowest[measure] and part >= 0:
            lowest[measure] = np.median(notes[measure, part])
    s = pd.Series()
    for ind, row in df.iterrows():
        s.loc[ind] = (notes[row['measure'], row['part']]
                      == lowest[row['measure']]) * 1
    return s


def entrance_effect(df):
    s = pd.Series()
    last_time = defaultdict(lambda: 0)
    current_time = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        if row['measure'] + row['offset'] > current_time[row['part']]:
            last_time[row['part']] = row['measure'] + row['offset']
        s.loc[ind] = row['measure'] + row['offset'] - last_time[row['part']]
        current_time[row['part']] = max(
            current_time[row['part']], row['measure'] + row['offset'] + row['duration'].quarterLength)
    return s


def harmony(df):
    s = pd.Series()
    for ind, row in df.iterrows():
        s.loc[ind] = 1
    return s


def highest(df):
    s = pd.Series()
    ps = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        if row['x_train'] == 0:
            continue
        if row['ps'] > ps[(row['measure'], row['offset'])]:
            ps[(row['measure'], row['offset'])] = row['ps']
    for ind, row in df.iterrows():
        s.loc[ind] = (row['ps'] == ps[(row['measure'], row['offset'])]) * 1
    return s


def occurrence(df):
    s = pd.Series()
    counts = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        if row['x_train'] == 0:
            continue
        counts[row['measure'], row['part'], row['pitch'].name] += 1
    highest = defaultdict(lambda: 2)
    for measure, part, name in counts:
        highest[measure, part] = max(
            highest[measure, part], counts[measure, part, name])
    for ind, row in df.iterrows():
        s.loc[ind] = (counts[row['measure'], row['part'], row['pitch'].name]
                      == highest[row['measure'], row['part']]) * 1
    return s


def offset_value(df):
    s = pd.Series()
    for ind, row in df.iterrows():
        s.loc[ind] = row['measure'] + row['offset']
    return s


def onset_after_rest(df):
    s = pd.Series()
    current_time = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        s.loc[ind] = (row['measure'] + row['offset']
                      > current_time[row['part']]) * 1
        current_time[row['part']] = max(
            current_time[row['part']], row['measure'] + row['offset'] + row['duration'].quarterLength)
    return s


def pitch_distance(df):
    s = pd.Series()
    for ind, row in df.iterrows():
        s.loc[ind] = abs(row['ps'] - 60)
    return s


def rhythm_variety(df):
    s = pd.Series()
    current_time = defaultdict(lambda: 0)
    last_length = defaultdict(lambda: 0)
    last_index = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        s.loc[ind] = (row['measure'] + row['offset']
                      > current_time[row['part']]) * 1
        if row['duration'].quarterLength != last_length[row['part']]:
            s.loc[ind] = 1
            s.loc[last_index[row['part']]] = 1
        current_time[row['part']] = max(
            current_time[row['part']], row['measure'] + row['offset'] + row['duration'].quarterLength)
        last_length[row['part']] = row['duration'].quarterLength
        last_index[row['part']] = ind
    return s


def strong_beats(df):
    return df['offset'].apply(lambda x: (float(x)).is_integer())


def sustained_rhythm(df):
    counts = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        counts[row['measure'], row['part']] += 1
    least = defaultdict(lambda: 10000)
    for measure, part in counts:
        if counts[measure, part] < least[measure] and part >= 0:
            least[measure] = counts[measure, part]
    s = pd.Series()
    for ind, row in df.iterrows():
        s.loc[ind] = (counts[row['measure'], row['part']]
                      == least[row['measure']]) * 1
    return s


def vertical_doubling(df):
    stats = defaultdict(lambda: 0)
    for ind, row in df.iterrows():
        if row['x_train'] == 0:
            continue
        stats[(row['measure'], row['pitch'].name)] += 1
    s = pd.Series()
    for ind, row in df.iterrows():
        s.loc[ind] = (stats[(row['measure'], row['pitch'].name)] > 1) * 1
    return s


def duration_length(df):
    return df['duration'].apply(lambda x: x.quarterLength)

# %%
