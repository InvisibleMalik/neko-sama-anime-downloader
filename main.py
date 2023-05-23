import os
import nekosama
from time import time, sleep
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tqdm import tqdm
import threading

client = nekosama.Client()

# Function to handle the download button click
def download_episodes():
    query = entry_query.get()
    if not query.startswith('https://'):
        animes = client.search(query, limit=10)
        # Update GUI to show anime search results
        anime_list.delete(0, tk.END)
        for i, a in enumerate(animes):
            anime_list.insert(tk.END, f'{i}. {a.name}')
        anime_list.select_set(0)
    else:
        anime = client.get_anime(query)
        # Update GUI with selected anime information
        selected_anime_label.config(text=f'Selected Anime: {anime.title}')
        total_episodes_label.config(text=f'Total Episodes: {len(anime.episodes)}')
        start = 0  # Default start range
        episodes = anime.episodes[start:]
        path = filedialog.askdirectory()
        if path:
            # Update GUI to show download progress
            download_button.config(state=tk.DISABLED)
            status_label.config(text='Downloading...')
            root.update_idletasks()

            if not os.path.exists(path):
                os.mkdir(path)

            if not path.endswith(('/', '\\')):
                path += '/'

            timeout = 5  # Default request timeout
            backend = 'ffmpeg'  # Default backend

            episode_count = len(episodes)
            progress_bar.config(maximum=episode_count, value=0)

            # Create a thread to run the download process in the background
            download_thread = threading.Thread(target=download_episodes_thread, args=(episodes, path, backend, timeout, episode_count))
            download_thread.start()

# Function to handle the download process in a separate thread
def download_episodes_thread(episodes, path, backend, timeout, episode_count):
    for i, episode in enumerate(tqdm(episodes, desc='Downloading', unit=' episode', ncols=80)):
        episode_start_time = time()
        file_name = f'{episode.name}.mp4'  # Set the file name
        file_path = os.path.join(path, file_name)
        episode.download(file_path,
                         method=backend, callback=debug, quiet=True)
        sleep(timeout)
        progress_bar.config(value=i+1)
        root.update_idletasks()

        # Calculate episode size and update status label
        episode_size = os.path.getsize(file_path)
        episode_size_mb = round(episode_size / (1024 * 1024), 2)
        status_label.config(text=f'Downloaded: {episode.name} - {episode_size_mb} MB')
        root.update_idletasks()

    status_label.config(text='Download completed!')
    root.update_idletasks()
    download_button.config(state=tk.NORMAL)

# Function for the download progress callback
def debug(status, current, total):
    # Update GUI to show the download progress
    status_label.config(text=f'Downloading... {current}/{total} ({round(current/total*100, 2)}%)')
    root.update_idletasks()

# Create the GUI
root = tk.Tk()
root.title('Anime Downloader')

# Query input
label_query = tk.Label(root, text='Enter query or URL:')
label_query.pack()
entry_query = tk.Entry(root, width=50)
entry_query.pack()

# Download button
download_button = tk.Button(root, text='Download', command=download_episodes)
download_button.pack()

# Selected Anime label
selected_anime_label = tk.Label(root, text='')
selected_anime_label.pack()

# Total Episodes label
total_episodes_label = tk.Label(root, text='')
total_episodes_label.pack()

# Progress bar
style = ttk.Style()
style.theme_use('clam')
style.configure("custom.Horizontal.TProgressbar", thickness=10, troughcolor='white', background='#8dc63f', troughrelief='flat')
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate', style="custom.Horizontal.TProgressbar")
progress_bar.pack()

# Status label
status_label = tk.Label(root, text='')
status_label.pack()

# Run the GUI
root.mainloop()