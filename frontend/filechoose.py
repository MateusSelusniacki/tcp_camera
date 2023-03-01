from plyer.platforms.win.filechooser import WinFileChooser

class FileChooser(WinFileChooser):
    def open_file(self, *args, **kwargs):
        return self._file_selection_dialog(mode="open", *args, **kwargs)

    def save_file(self, *args, **kwargs):
        return self._file_selection_dialog(mode="save", *args, **kwargs)

    def choose_dir(self, *args, **kwargs):
        return self._file_selection_dialog(mode="dir", *args, **kwargs)