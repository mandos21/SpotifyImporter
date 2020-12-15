import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from PIL import ImageTk, Image
import requests
from io import BytesIO
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tinytag import TinyTag
import threading
import credentials

class main_window:

    def __init__(self):

        client_credentials_manager = SpotifyClientCredentials(credentials.client_id,credentials.client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        self.items_to_save = []

        # Init Main Window
        self.main_window = tk.Tk()
        self.menu_bar = tk.Menu(self.main_window)
    
        # Init Menu Bar
        self.file_menu = tk.Menu(self.menu_bar,tearoff=0)
        self.file_menu.add_command(label="Open", command=self.fileSelector)
        
        # Init Menu Bar Items
        self.menu_bar.add_cascade(label="File",accelerator="CTRL+F",menu=self.file_menu)
        self.main_window.config(menu=self.menu_bar)

        # Init Main Frame
        self.main_frame = tk.Frame(self.main_window)
        self.main_frame.pack()

        # Init Sub Frames
        self.art_frame = tk.LabelFrame(self.main_frame,text="Album Art",width=250,height=250)
        self.matches_frame = tk.LabelFrame(self.main_frame,text="Potential Matches",width=500,height=150)
        self.file_details_frame = tk.LabelFrame(self.main_frame,text="File Metadata",width=250,height=125)
        self.match_details_frame = tk.LabelFrame(self.main_frame,text="Match Details",width=250,height=125)
        self.song_details_frame = tk.LabelFrame(self.main_frame,text="Songs",width=500,height=250)
        self.album_select_frame = tk.LabelFrame(self.main_frame,text="Album Selection",width=500,height=50)

        # Initialize Album Image
        self.art_frame.pack_propagate(0)
        self.img = Image.open(BytesIO(requests.get('https://i.scdn.co/image/ab67616d0000b273adb1732fa8d44b8eb2f6c0bf').content))
        self.img = self.img.resize((240,240), Image.ANTIALIAS)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.img_panel = tk.Label(self.art_frame,image = self.tk_img) 
        self.img_panel.pack()

        # Initialize Matches Listbox
        self.matches_frame.pack_propagate(0)
        self.columns = ['Album','Artist','Year']
        self.match_view = ttk.Treeview(self.matches_frame,columns=self.columns,show='headings',selectmode='browse')

        self.match_view.column(0,width=200)
        self.match_view.column(1,anchor=tk.CENTER,width=200)
        self.match_view.column(2,anchor=tk.E,width=87)


        for i in range(0,3):
            self.match_view.heading(i,text=self.columns[i])

        self.match_view.bind("<<TreeviewSelect>>",self.onSelect)
        self.match_view.pack(pady=2)



        # Initialize Songs Listbox Area
        self.song_listbox = tk.Listbox(self.song_details_frame,selectmode='multiple',width=41)
        self.song_listbox.grid(row=0,column=0,columnspan=2,rowspan=2)

        self.right_area = tk.Frame(self.song_details_frame)
        self.right_area.grid(row=0,column=2)

        self.select_all_button = ttk.Button(self.song_details_frame,text='Select All',width=20,takefocus=False,command=self.select_all)
        self.select_none_button = ttk.Button(self.song_details_frame,text='Select None',width=19,takefocus=False,command=self.select_none)

        self.select_all_button.grid(row=2,column=0)
        self.select_none_button.grid(row=2,column=1)

        #self.right_subarea = tk.Frame(self.right_area)

        self.selection_explan = tk.Label(self.song_details_frame,text="\n\nSongs selected in the box to the left \nwill be added to your saved songs once \nall albums have been viewed\n if this album is saved.\n\n\n",width=34)


        self.save_album_button = ttk.Button(self.song_details_frame,text="Don't Save This Album",width=39,takefocus=False,command=self.album_toggle)
        self.save_artist_button = ttk.Button(self.song_details_frame,text="Save This Artist",width=39,takefocus=False,command=self.artist_toggle)

        self.selection_explan.grid(row=0,column=3)
        #self.select_all_button.pack(side=tk.LEFT)
        #self.select_none_button.pack(side=tk.LEFT)
        #self.right_subarea.pack()
        self.save_album_button.grid(row=1,column=3)
        self.save_artist_button.grid(row=2,column=3)




        # Initialize File Details 
        self.file_details_frame.grid_propagate(0)

        self.file_folder_label = tk.Label(self.file_details_frame,text="Folder: ",font='Arial 8 bold',anchor=tk.W,width=10)
        self.file_name_label = tk.Label(self.file_details_frame,text="Example File: ",font='Arial 8 bold',anchor=tk.W,width=10)
        self.file_artist_label = tk.Label(self.file_details_frame,text="Artist: ",font='Arial 8 bold',anchor=tk.W,width=10)
        self.file_album_label = tk.Label(self.file_details_frame,text="Album: ",font='Arial 8 bold',anchor=tk.W,width=10)
        self.file_year_label = tk.Label(self.file_details_frame,text="Year: ",font='Arial 8 bold',anchor=tk.W,width=10)

        self.file_folder_contents = tk.Label(self.file_details_frame,text="Ok Computer Folder",anchor=tk.E,width=22)
        self.file_name_contents = tk.Label(self.file_details_frame,text="00 - Airbag.flac",anchor=tk.E,width=22)
        self.file_artist_contents = tk.Label(self.file_details_frame,text="Radiohead",anchor=tk.E,width=22)
        self.file_album_contents = tk.Label(self.file_details_frame,text="Ok Computer",anchor=tk.E,width=22)
        self.file_year_contents = tk.Label(self.file_details_frame,text="1997",anchor=tk.E,width=22)

        self.file_folder_label.grid(row=0,column=0)
        self.file_name_label.grid(row=1,column=0)
        self.file_artist_label.grid(row=2,column=0)
        self.file_album_label.grid(row=3,column=0)
        self.file_year_label.grid(row=4,column=0)

        self.file_folder_contents.grid(row=0,column=1)
        self.file_name_contents.grid(row=1,column=1)
        self.file_artist_contents.grid(row=2,column=1)
        self.file_album_contents.grid(row=3,column=1)
        self.file_year_contents.grid(row=4,column=1)


        # Initialize Match Details
        self.match_details_frame.pack_propagate(0)
        self.match_album = tk.Label(self.match_details_frame,text="No Albums Loaded",font='Arial 12 bold',wraplength=200)
        self.match_artist_year = tk.Label(self.match_details_frame,text="Load your albums folder from the files menu.  The anticipated directory structure is music/album/songs",font='Arial 11',wraplength=240)

        self.match_album.pack()
        self.match_artist_year.pack()

        # Initialize Album Select Area
        self.album_select_frame.grid_propagate(0)

        # I hate that I need to do this
        self.filler_space1 = tk.Label(self.album_select_frame,text="                                       ")
        self.filler_space2 = tk.Label(self.album_select_frame,text="                                      ")

        self.progress_text = tk.Label(self.album_select_frame,text="0 of 0",font='Arial 10 bold',width=13)

        self.prev_button = ttk.Button(self.album_select_frame,text="<<",width=10,takefocus=False,command=self.prev_album)
        self.next_button = ttk.Button(self.album_select_frame,text=">>",width=10,takefocus=False,command=self.next_album)


        
        self.prev_button.grid(row=0,column=0)
        self.filler_space1.grid(row=0,column=2)
        self.progress_text.grid(row=0,column=3)
        self.filler_space2.grid(row=0,column=4)
        self.next_button.grid(row=0,column=6)


        # Grid Sub Frames
        self.art_frame.grid(row=0,column=0,rowspan=2,sticky=tk.E)
        self.match_details_frame.grid(row=0,column=1,sticky=tk.NW)
        self.matches_frame.grid(row=2,column=0,columnspan=2,sticky=tk.N,padx=3)
        self.file_details_frame.grid(row=1,column=1,sticky=tk.NW)
        self.song_details_frame.grid(row=3,column=0,columnspan=2,sticky=tk.N)
        self.album_select_frame.grid(row=4,column=0,columnspan=2,sticky=tk.N)


        #self.load_folders("X:\\mandos\\Nextcloud\\Music\\")
        

       
    def prev_album(self):
        print(self.index)
        if self.index > 1:
            self.index -= 2
            self.next_album()

    def next_album(self):
        index = self.index

        print("index: " + str(index))
        print("big_matches_list: " + str(len(self.big_matches_list)))
        if index <= len(self.big_matches_list):

            progress_text = self.progress_text.cget('text').split(' ')
            progress_text[0] = str(index+1)
            progress_text[2] = str(len(self.big_matches_list))

            self.progress_text.config(text=' '.join(progress_text))

            if self.save_album_button.cget("text") == "Don't Save This Album" and index != 0:
                selected_songs = self.song_listbox.curselection()

                saved_songs = [{'song':self.songs[i][0],'songid':self.songs[i][1]} for i in selected_songs if self.song_listbox.get(i) == self.songs[i][0]]
                albumid = self.matches_list[0][int(self.match_view.selection()[0])][3]
                album = self.matches_list[0][int(self.match_view.selection()[0])][0]

                artistid = ""
                artist = ""
                if self.save_artist_button.cget("text") == "Don't Save This Artist":
                    artistid = self.matches_list[0][int(self.match_view.selection()[0])][5]
                    artist = self.matches_list[0][int(self.match_view.selection()[0])][1]

                saved_items = {'album':album,'albumid':albumid,'artist':artist,'artistid':artistid,'songs':saved_songs}
                print(saved_items)

                self.items_to_save.append(saved_items)

            self.save_album_button.config(text="Don't Save This Album")
            self.save_artist_button.config(text="Save This Artist")

            if index < len(self.big_matches_list):
                self.matches_list = self.big_matches_list[index]
                self.clear_treeview()
                for i, match in enumerate(self.matches_list[0]):
                    self.match_view.insert('','end',id=str(i),values=(match[0],match[1],match[2]))

                self.set_file_details(self.matches_list[1])
                self.match_view.selection_set(self.match_view.get_children()[0])
                self.onSelect(self)
                


        if self.index >= len(self.big_matches_list)-1:
            self.next_button.config(text="Review")
        else:
            self.next_button.config(text=">>")

        if self.index >= len(self.big_matches_list):
            self.review_screen()

        self.index += 1


    def review_screen(self):
        print(self.items_to_save)
        self.main_frame.destroy()

        self.tree = ttk.Treeview(self.main_window)

        self.tree["columns"] = ("Type", 'ID')
        self.tree.column("Type",anchor='e',width=5)
        self.tree.column("ID",anchor='e',width=15)

        self.tree.heading("Type", text="Type")
        self.tree.heading("ID", text="ID")

        self.vsb = ttk.Scrollbar(self.tree,orient="vertical",command=self.tree.yview)
        self.vsb.pack(anchor='e',fill='y',expand=True,side='right')
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.tree.pack(expand=True, fill='both')

        self.state = True

        for item in self.items_to_save:
            self.tree.insert('','end',item['album'],text=item['album'],values=['album',item['albumid']],open=True,tags=('unfinished','album'))
            if item['artist']:
                self.tree.insert(item['album'],'end',text=item['artist'],values=['artist',item['artistid']],open=True,tags=('artist','unfinished'))

            if item['songs']:
                for song in item['songs']:
                    self.tree.insert(item['album'],'end',text=song['song'],values=['song',song['songid']],open=True,tags=(str(self.state),'unfinished'))
                    self.state = not self.state
                self.state = True


        self.tree.tag_configure('True',background='slategray2')
        self.tree.tag_configure('album',background='skyblue3')
        self.tree.tag_configure('artist',background='skyblue2')
        self.tree.tag_configure('False',background='slategray1')
        self.tree.tag_configure('finished',background='green')



    def set_file_details(self,album_details):
        self.file_folder_contents.config(text=album_details[1])
        self.file_name_contents.config(text=album_details[0])
        self.file_artist_contents.config(text=album_details[2].artist)
        self.file_album_contents.config(text=album_details[2].album)
        self.file_year_contents.config(text=album_details[2].year)


    def clear_treeview(self):
        children = self.match_view.get_children()

        for child in children:
            self.match_view.delete(child)


    def album_toggle(self):
        if self.save_album_button.cget("text") == "Save This Album":
            self.save_album_button.config(text="Don't Save This Album")
        else:
            self.save_album_button.config(text="Save This Album")
            

    def artist_toggle(self):
        if self.save_artist_button.cget("text") == "Save This Artist":
            self.save_artist_button.config(text="Don't Save This Artist")
        else:
            self.save_artist_button.config(text="Save This Artist")

    def select_none(self):
        if len(self.song_listbox.curselection()) >0:
            self.song_listbox.selection_clear(0,self.song_listbox.size())

    def select_all(self):
            self.song_listbox.selection_set(0,self.song_listbox.size())

    def info_update(self,info_list):
        self.match_album.config(text=info_list[0])
        self.match_artist_year.config(text=info_list[1]+" - "+info_list[2])
        self.set_songs(info_list[3])
        self.set_art(info_list[4])

    def set_art(self,art_link):
        image = Image.open(BytesIO(requests.get(art_link).content))
        image= image.resize((240,240),Image.ANTIALIAS)
        tk_image = ImageTk.PhotoImage(image)
        self.img_panel.config(image=tk_image)
        self.img_panel.image = tk_image


    def set_songs(self,album_id):
        self.song_listbox.delete(0,'end')
        self.songs = self.get_tracks(album_id)
        for song in self.songs:
            self.song_listbox.insert(tk.END,song[0])


    def onSelect(self,parent):
        select_index = self.match_view.selection()
        selection_detail = self.matches_list[0][int(select_index[0])]
        print(selection_detail)
        self.info_update(selection_detail)


    def fileSelector(self):
        self.music_dir = filedialog.askdirectory(title="Select Music Directory")
        self.load_folders(self.music_dir)


    def get_tracks(self,album_id):
        album_info = self.sp.album_tracks(album_id)['items']
        tracks = []
        for track in album_info:
            tracks.append([track['name'],track['id'],track['artists'][0]['id']])
        return tracks


    def load_folders(self,folder):

        self.folder = folder

        def kill_window():
            self.loading_window.destroy()
            self.main_window.wm_attributes("-disabled",False)

        def real_load_folders():

            valid_exts = ['MP3','FLAC','M4A']
            self.albums = []
            self.big_matches_list = []
            for folder in [ f.path for f in os.scandir(self.folder) if f.is_dir() ]:
                try:
                    for file in os.scandir(folder):
                        if file.name.split('.')[-1].upper() in valid_exts:
                            self.albums.append((file.name,folder.split("\\")[-1],TinyTag.get(file.path)))
                            break
                        
                except:
                    print("You probably made this folder on linux, dumbass")


            for album in self.albums:
                 match= self.album_search(album[2].artist,album[2].album)
                 if len(match) != 0:
                    self.big_matches_list.append([match,album])

            self.ok_button.config(state='active')
            self.load_button.config(state='disabled')

            self.index = 0

            self.next_album()

            self.match_view.selection_set("0")
            self.onSelect(self)



        self.loading_window = tk.Tk()
        #self.main_window.wm_attributes("-disabled",True)
        self.loading_label = tk.Label(self.loading_window,text="Press the button to gather data from music folder and query spotify API\nPlease be patient, this can take a while")
        self.load_button = ttk.Button(self.loading_window,text="Load",command=real_load_folders)
        self.ok_button = ttk.Button(self.loading_window,text="Okay",state='disabled',command=kill_window)

        self.loading_label.pack()
        self.load_button.pack()
        self.ok_button.pack()




    def album_search(self,artist,album):
        search = self.sp.search(q=str(artist + " " + album),type='album')
        album_list = []
        for i in range(0,len(search['albums']['items'])):
            item = search['albums']['items'][i]
            #print(item)
            album_list.append([item['name'],item['artists'][0]['name'],item['release_date'],item['id'],item['images'][0]['url'],item['artists'][0]['id']])
        return album_list


main_window()
    
    