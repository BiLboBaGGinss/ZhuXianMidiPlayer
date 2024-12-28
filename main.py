import pretty_midi
from pynput.keyboard import Controller, Key
import time
from bisect import bisect_left
from tkinter import Tk, filedialog

# 键盘映射
KEY_MAP = {
    72: '1',  # C5
    74: '2',  # D5
    76: '3',  # E5
    77: '4',  # F5
    79: '5',  # G5
    81: '6',  # A5
    83: '7',  # B5

    60: 'q',  # C4
    62: 'w',  # D4
    64: 'e',  # E4
    65: 'f',  # F4
    67: 't',  # G4
    69: 'y',  # A4
    71: 'u',  # B4

    48: 'a',  # C3
    50: 's',  # D3
    52: 'd',  # E3
    53: 'f',  # F3
    55: 'g',  # G3
    57: 'h',  # A3
    59: 'j',  # B3
}

# 确定音域范围
MIN_MIDI_NOTE = min(KEY_MAP.keys())
MAX_MIDI_NOTE = max(KEY_MAP.keys())

def transpose_note(note_pitch):
    """将音符移调至指定音域内"""
    if note_pitch < MIN_MIDI_NOTE:
        while note_pitch < MIN_MIDI_NOTE:
            note_pitch += 12
    elif note_pitch > MAX_MIDI_NOTE:
        while note_pitch > MAX_MIDI_NOTE:
            note_pitch -= 12
    return note_pitch

def closest_note(note_pitch, keys=sorted(KEY_MAP.keys())):
    """找到最接近给定音符的已映射音符"""
    pos = bisect_left(keys, note_pitch)
    if pos == 0:
        return keys[0]
    if pos == len(keys):
        return keys[-1]
    before = keys[pos - 1]
    after = keys[pos]
    if after - note_pitch < note_pitch - before:
        return after
    else:
        return before

def get_key_for_note(note_pitch):
    """获取给定音符对应的键盘键，使用最近邻原则处理未映射音符"""
    adjusted_pitch = transpose_note(note_pitch)
    if adjusted_pitch in KEY_MAP:
        return KEY_MAP[adjusted_pitch]
    else:
        nearest_note = closest_note(adjusted_pitch)
        print(f"Note {note_pitch} not found, using nearest note {nearest_note}.")
        return KEY_MAP[nearest_note]

def create_event_list(midi_data):
    events = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            key = get_key_for_note(note.pitch)
            if key is not None:
                events.append((note.start, 'press', key))
                events.append((note.end, 'release', key))
            else:
                print(note.pitch)
    events.sort()  # 按照时间排序
    return events

def play_events(events):
    keyboard = Controller()
    start_time = time.perf_counter()

    for event_time, action, key in events:
        elapsed_time = time.perf_counter() - start_time
        sleep_time = event_time - elapsed_time

        if sleep_time > 0:
            time.sleep(sleep_time)

        if action == 'press':
            keyboard.press(key)
            print(f"Press {key} at time {event_time:.3f}")
        elif action == 'release':
            keyboard.release(key)
            print(f"Release {key} at time {event_time:.3f}")

def select_file():
    root = Tk()  # 创建Tkinter主窗口
    root.withdraw()  # 隐藏主窗口

    file_path = filedialog.askopenfilename()  # 打开文件选择对话框
    return file_path

def play_midi_file(midi_file_path):
    midi_data = pretty_midi.PrettyMIDI(midi_file_path)
    events = create_event_list(midi_data)
    play_events(events)

if __name__ == "__main__":
    midi_file = select_file()
    print('切换回游戏窗口3秒后开始演奏')
    time.sleep(3)
    play_midi_file(midi_file)