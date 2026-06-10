def create_concat_file(segment_files, filename="concat_list.txt"):
    with open(filename, "w") as f:
        for file in segment_files:
            f.write(f"file '{file}'\n")

    return filename
