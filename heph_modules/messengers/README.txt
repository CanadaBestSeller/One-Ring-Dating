So here's how this interface/implementation system works:

- All the dating platforms (OKC, Tinder, etc.) will have their own implementations of Messenger
- Every implementation MUST have a method called send_message(message, profile_raw_text, blacklist_folder_path)
