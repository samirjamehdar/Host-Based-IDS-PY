# Host-baserad IDS
# Samir Jamehdar
# All the comments are in swedish and serve the purpose of being notes for myself.


import os
import hashlib


def find_subdirs(directory):
    """
    Returns a list with all
    subdirectories.
    """
    sub_dirs = []
    paths = os.listdir(directory)   # Gör en lista med alla filer i mappen
    
    for path in paths:       # Inser att detta är ett dumt variabel namn
        fullpath = directory + '/' + path   # Här får jag absoluta sökvägen som jag sedan använder

        if os.path.isdir(fullpath): # Här kollar jag om det är en mapp eller en vanlig fil, om det är en mapp så lägger jag till
                                        # Sökvägen i min lista sub_dirs.
            sub_dirs.append(fullpath)
            # Nu ska jag gå ner i undermappar och då är rekursion smart
            sub_dirs += find_subdirs(fullpath)  # här använder jag rekursion genom att i princip öppna alla subdirs och appenda dom till min lista

    return sub_dirs



def dir_structure(directory, subdir_lst):
    """
    Returns a dictionary of all files in a directory/subdirectories
    """


    dir_dict = {}

    current_dir = os.listdir(directory) # En lista med allt som finns i första directorien där jag börjar min sökning
    dir_dict[directory] = current_dir   # Lägger directorien där jag börjar min sökning/scanning

    for path in subdir_lst:
        dir_dict[path] = os.listdir(path)   # för varje subdir blir en nyckel med innehållet som value i min dict
    
    return dir_dict



def absolute_and_relative_lst(dir_dict):
    """
    Returns two lists, a relative and absolute
    pathway for all the files.
    """

    absolute_paths = []
    relative_paths = []


    for i in dir_dict:  # Kollar directories med i och filnamn med j
        for j in dir_dict[i]:
            if not os.path.isdir(i + '/' +j):   # lägger bara till i listan om det är en fil (får ej vara map)
                relative_paths.append(j)
                absolute_paths.append(i + '/' + j)  # Här får jag en lista med alla absoluta sökvägar 

    
    return absolute_paths, relative_paths



def hash_files_lst(absolute_lst):
    """
    Takes a list with absolute pathways
    and hashes the files (does not hash directories)
    """
    # Tar in den absoluta sökvägen till alla filer som förekommer i den önskade mappen och hashar dem med
    # Sha1

    hashed_lst = []

    for files in absolute_lst:

        infile = open(f'{files}', 'rb') # öppnar filerna och hashar innehållet
        infile_read = infile.read()
        infile.close

        infile_hash = hashlib.sha1(infile_read)
        hashed_lst.append(infile_hash.hexdigest())

    return hashed_lst   # returnerar en lista med alla hashade objekt.



def merge_relative_hash(hash_lst, relative_paths_lst):
    """
    Converts and merges two lists
    to a dictionary as key:value pairs.
    """

    relative_paths = relative_paths_lst
    merged_dict = {}

    for i in range(0, len(hash_lst)):
        merged_dict[relative_paths[i]] = hash_lst[i]
    
    return merged_dict  # Här tar jag den hashade listan och relativa sökvägen,
    #   Det smidiga här är att dessa kommer ha samma indexering så jag kan göra en dict med dom
    #  Där key är namnet på filen (relative pathway), och value blir hashsumman



def write_first_log(merged_dict):
    """
    Writes the first log file.
    """
    # Skapar den första loggen "IDSlog.txt"
    outfile = open('IDSlog.txt', 'x') # x kommer ge error om filen redan finns som jag sedan fångar-
    outfile.write(f'{merged_dict}')         # och då vet jag att filen redan finns och att jag kan jämföra den gamla loggen
    outfile.close() 



def compare_log(merged_dict):
    """
    Compares the old log file (IDSlog.txt)
    with current scanned directories.
    Returns three lists for changed files
    removed files and added files.
    """


    infile = open('IDSlog.txt', 'r')
    old_log_file = infile.read()
    infile.close()

    old_log = eval(old_log_file)    # Gör om en sträng till ett uttryck, i detta fallet får jag alltså en dictionary
    new_log = merged_dict

    changes = []
    new_added = []
    removed = []

    if new_log == old_log:  # här har inga förändringar skett och då kan vi returnera direkt.
        return changes, new_added, removed
    
    else:   # Här itererar jag över gamla och nya logen för att kolla efter saker som har ändrats
        for filename in new_log:
            if filename not in old_log:
                new_added.append(filename)

        for filename in old_log:
            if filename not in new_log:
                removed.append(filename)
        
        for hashsum in old_log:
            if hashsum in new_log:
                if old_log[hashsum] != new_log[hashsum]:
                    changes.append(hashsum)
    
    # Converting lists to strings           Konverterar mina listor till strängar, separerar elementen med kommetecken och mellanslag
    changes_str = ', '.join([str(elem) for elem in changes])   
    new_added_str = ', '.join([str(elem) for elem in new_added])
    removed_str = ', '.join([str(elem) for elem in removed])

    return changes_str, new_added_str, removed_str



def main():

    os.system("clear")  # Gör det fint i terminalen och clearar den
    usr_inp_isdir = False

    while not usr_inp_isdir:
        print('Enter the absolute path to a directory to scan')
        user_input = input('Absolute path: ')
        absolute_path = f'{user_input}'

        try:
            sub_dirs = find_subdirs(absolute_path)
        except FileNotFoundError:
            print('The directory does not exist, please try again!\n')
        except NotADirectoryError:
            print('The file os not a directory, please try again!\n')
        except:
            print('Incorrect input, please try again!\n')
        else:
            if len(absolute_path) == absolute_path.count('/'):
                print('\nIncorrect input, please try again!\n')
            elif len(absolute_path) == absolute_path.count('.'):
                print('\nIncorrect input, please try again!\n')
            else:
                usr_inp_isdir = True


    sub_dirs_dict = dir_structure(absolute_path, sub_dirs)
    absolute_lst, relative_lst = absolute_and_relative_lst(sub_dirs_dict)
    hashed_lst = hash_files_lst(absolute_lst)
    merged_dict = merge_relative_hash(hashed_lst, relative_lst)


    try:
        write_first_log(merged_dict)
        print('______________________________________________')
        print('A log file has successfully been created.')
        print('To scan for changes, run the IDS script again.')
        print('______________________________________________')
    except FileExistsError:
        changes, new_added, removed = compare_log(merged_dict)

        if len(changes) + len(new_added) + len(removed) == 0:
            print('The files have not changed since the last run')
        else:
            print('Analysis of the directory since the last run')
            print('_'*50)
            print('\tFiles that have changed:\n' + changes)
            print('_'*50)
            print('\tFiles that have been newly added:\n' + new_added)
            print('_'*50)
            print('\tFiles that have been removed:\n' + removed)
            print('_'*50)

main()


# eval funktionen tar en  ”Sträng” som argument och returnerar resultatet som ett uttryck


