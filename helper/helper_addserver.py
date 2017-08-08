from api.utils.config import SERVER_LIST,USER_DICT,LOCAL_MNT_DIR, FILE_LOCATION, ZONE_DICT, ZONE_SLAVES, LOG_DIR, REMOTE_MNT_DIR, LOCAL_MNT_DIR
import sys
import shutil



# Main Method
def main():
    print "----------------------------------------"
    print "   DNSAPI - helper_addserver.py"
    print "----------------------------------------"
    if len(sys.argv) == 1:
        print "See usage : helper_addserver.py --help"

    else:
        if str(sys.argv[1]) == "--list":
            print " Server List : "+str(len(ZONE_DICT))
            for server in SERVER_LIST:
                print "   - "+server+" : ["+USER_DICT[server]+","+LOCAL_MNT_DIR[server]+"]"

        if str(sys.argv[1]) == "--add":
            if len(sys.argv) == 5:
                append_data()
            else:
                print "Failed to Add. \nSee usage : helper_addserver.py --help"

        if str(sys.argv[1]) == "--help":
            print "  These are main command usage of this dnsapi add server helper:\n"
            print "     --list     View list of available server in formats :"
            print "\t\treturn :--> {{server_ip}} : [ {{user}},{{mount_directory}} ]"
            print "\n"
            print "     --add      Add new server with required parameter : server_ip, user, and mount_dir"
            print "\t\tusage --> helper_addserver.py --add {{server_ip}} {{user}} {{mount_directory}}"
            print "\n"
            print "     --help     This help command usage."

# Method append data to SERVER_LIST, USER_DICT, LOCAL_MNT_DIR
def append_data():
    check_udict = False
    check_list = False
    check_mntdir = False
    check_udict_index = 0
    check_mntdir_index = 0

    # Argument data
    VAR_DATA=sys.argv[2]
    VAR_USER=sys.argv[3]
    VAR_MNT_DIR=sys.argv[4]

    # Open File to parse and config
    print "    Open file... \n    Add Data... "
    file_path = '../api/utils/config.py'
    shutil.copyfile(file_path,file_path+'.bak')
    with open(file_path+'.bak', 'r') as readfile, open(file_path, 'w') as outfile:
        for line in readfile:
            # Add to SERVER_LIST
            if check_list==True:
                if "," in line:
                    """skip upper data with comma."""
                elif "]" in line:
                    line='\n\t"'+VAR_DATA+'" \n]\n'
                    check_list=False
                else:
                    line=line.rstrip()+','

            if "SERVER_LIST = [" in line:
                check_list = True
            #End of SERVER_LIST append

            # Add to USER_DICT
            if check_udict==True:
                if "," in line:
                    """skip upper data with comma."""
                elif "}" in line:
                    line='\n\tSERVER_LIST['+str(check_udict_index)+']: "'+VAR_USER+'" \n}\n'
                    check_udict=False
                else:
                    line=line.rstrip()+','
                check_udict_index=check_udict_index+1

            if "USER_DICT = {" in line:
                check_udict = True
            #End of USER_DICT append

            # Add to LOCAL_MNT_DIR
            if check_mntdir==True:
                if "," in line:
                    """skip upper data with comma."""
                elif "}" in line:
                    line='\n\tSERVER_LIST['+str(check_mntdir_index)+']: "'+VAR_MNT_DIR+'" \n}\n'
                    check_mntdir=False
                else:
                    line=line.rstrip()+','
                check_mntdir_index=check_mntdir_index+1

            if "LOCAL_MNT_DIR = {" in line:
                check_mntdir = True
            #End of LOCAL_MNT_DIR append

            # Write line
            outfile.write(line)
    print "    Complete!"


# Call Default Main method
if __name__ == "__main__":
    main()
