def convert_sample_to_history_dialog(sample, with_knowledge=None):

    history_dialog = "History Dialogue:\n"
    for turn in sample["dialogue"]:
        history_dialog += f"{turn[0]}" +"\n"
        if turn[1] == "":
            ## NO GENERATION REQUIRED
            pass
        else:
            history_dialog += f"{turn[1]}" +"\n\n"
    # print("history:"+'\n'+history_dialog)

    return history_dialog