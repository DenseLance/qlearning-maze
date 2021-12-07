def reset_epoch():
    with open("current_epoch.txt", "w") as f:
        f.write("0")
        f.close()

def get_epoch():
    with open("current_epoch.txt", "r") as f:
        current_epoch = int(f.readline())
        f.close()
    return current_epoch

def add_epoch(final_epoch):
    with open("current_epoch.txt", "w") as f:
        f.write(str(final_epoch))
        f.close()

def create_log():
    with open("log.txt", "w") as f:
        f.write(f"epoch,number_of_actions,win\n")
        f.close()

def append_to_log(epoch, number_of_actions, win): # epoch: INTEGER, number_of_actions: INTEGER, win: BOOLEAN
    with open("log.txt", "a") as f:
        f.write(f"{epoch},{number_of_actions},{win}\n")
        f.close()

def get_exploration_rate():
    with open("exploration_rate.txt", "r") as f:
        exploration_rate = float(f.readline())
        f.close()
    return exploration_rate

def update_exploration_rate(exploration_rate):
    with open("exploration_rate.txt", "w") as f:
        f.write(str(exploration_rate))
        f.close()
