from collections import defaultdict
import sys
import datetime
import math

## input_itcont_location store the input path specify in the second argument
input_itcont_location =  sys.argv[1] #"/Users/yimingliu/Desktop/donation-analytics/input/itcont.txt" #sys.argv[1]

## input_itcont_location store the percentile file path specify in the third argument
input_percentile_location = sys.argv[2] #"/Users/yimingliu/Desktop/donation-analytics/input/percentile.txt" #sys.argv[2]

## output_location store the output file path specify in the forth argument
output_location = sys.argv[3] #"/Users/yimingliu/Desktop/donation-analytics/output/repeat_donors.txt" #sys.argv[3]

## cmte_id is a nested dictionary, 1st level key is the cmte_id, 2nd level key is
## tuple (year,zipcode) to store the contribution for specific cmte_id per year
## per zipcode
cmte_id_dict = defaultdict(lambda: defaultdict(lambda: []))

## donor_freq_dict is a dictionary store the frequency of each donor to check
## if donor is a repeat donor
donor_freq_dict = defaultdict(int)

## donor_first_time_info is a dictonary store the donor infomation when they first
## occur and the data in this dictionary will be delete when the donor occur again,
## which will save space
donor_first_time_info = {}

## donor_oldest_donate_date is a dictionary store the oldest occur date of each
## donor, only the record newer than the oldest occur date of a repeat donor will
## be outputted in case the data is list out of order
donor_oldest_donate_date = {}



## the function used to extract donor infomation from each line in the file
def extract_donation_info(line):

    ## extract the information from each line, if the any data not valid, the line will
    ## be ignored
    try:
        columns = [i.strip() for i in line.split("|")]
        cmte_id = columns[0]
        name = columns[7]
        zip_code = columns[10]
        transaction_date = columns[13]
        transaction_amount = columns[14]
        other_id = columns[15]
    except:
        return False

    ## other_id has to be empty to treat as a valid line
    if len(other_id) != 0:
        return False

    ## cmid, name, zip_code, transaction date and transaction amount cannot be empty
    ## otherwise, skip the line
    nonempty_fields = [columns[i] for i in [0, 7, 10, 13, 14]]
    for i in nonempty_fields:
        if len(i)==0:
            return False
    
    ## zip code has to be greater than 5 digits to be a valid line, and the system
    ## only need the first 5 digits
    if len(zip_code) < 5:
        return False
    zip_code = zip_code[:5]

    ## transaction date must be valid
    ## transaction amount must be a number
    try:
        donation_date = datetime.datetime.strptime(transaction_date, "%m%d%Y")
        donation_year = donation_date.year
        donation_time = datetime.datetime(donation_date.year,donation_date.month,donation_date.day)
        transaction_amount = float(transaction_amount)
    except ValueError:
        return False
    
    ## return a dictonary as the output of this function
    return {
        "cmte_id": cmte_id,
        "name": name,
        "zip_code": zip_code,
        "donation_year": donation_year,
        "transaction_amount": transaction_amount,
        "transaction_date": donation_time
    }

## Add the contribution information per zipcode per year into
## the dictionary once repeat donor is found
def add_to_cmte_dict(info):
    cmte_id_dict[(info["cmte_id"])][(info["zip_code"], info["donation_year"])].append(info["transaction_amount"])
    cmte_id_dict[(info["cmte_id"])][(info["zip_code"], info["donation_year"])].sort()

## Add the frequency by 1 for each donor
def add_donor_freq_dict(donor_key):
    donor_freq_dict[donor_key] += 1

## Add the donor and contricutioninfo to the dictionary if it is a first time donor
def add_to_donor_first_time_info(donor_key,info):
    donor_first_time_info[donor_key]=info

## Update the oldest occur time of each donor by compare the date of the contribution
## of the donor
def update_donor_oldest_donate_date(info):
    donor_key = (info["name"],info["zip_code"])

    ## if the donor already has record, compare the date
    if(donor_key in donor_oldest_donate_date):
        if(info["transaction_date"] < donor_oldest_donate_date[donor_key]):
            donor_oldest_donate_date[donor_key] = info["transaction_date"]

    ## if the donor not exist in the record, it means this is the oldest record
    else:
        donor_oldest_donate_date[donor_key] = info["transaction_date"]
    
            
## delete a donor info record if identify as a repeat donor and store it in a
## temporary variable
def pop_donor_first_time_info(donor_key):
    first_time_info = donor_first_time_info.pop(donor_key, None)
    return first_time_info

## calculate the running percentile using nearest rank method
def calculate_running_percentile(info,percentile):
    contribution_list = cmte_id_dict[(info["cmte_id"])][(info["zip_code"],info["donation_year"])]
    N=len(contribution_list)
    percentile_index = math.ceil(percentile/100*N)
    return contribution_list[percentile_index-1]

## calculate the total contributions of the recipient in a specific zipcode and
## calender year
def calculate_total_contribution(info):
    return sum(cmte_id_dict[(info["cmte_id"])][(info["zip_code"],info["donation_year"])])

## calculate the total transactions of the recipient in a specific zipcode and
## calender year
def calculate_total_transaction(info):
    return len(cmte_id_dict[(info["cmte_id"])][(info["zip_code"],info["donation_year"])])

## obtain all the information and store in a list
def get_output_info(info,percentile):
    running_percentile = round(calculate_running_percentile(info,percentile))
    total_contribution = round(calculate_total_contribution(info))
    total_transaction = calculate_total_transaction(info)
    return [str(info["cmte_id"]),str(info["zip_code"]),str(info["donation_year"]),
            str(running_percentile),str(total_contribution),
            str(total_transaction)]

## write the require information into the output path 
def output_recipient_info(output_info,output_file):
    output_line = "|".join(output_info)
    output_file.write(output_line + "\n")   

## check if the current repeat donor recorder is newer than the oldest record on file
## in case the record is list out of order
def check_if_newer_than_oldest_record(info,donor_key):
    if (donor_key not in donor_oldest_donate_date):
        return 1
    else:
        return info["transaction_date"] >= donor_oldest_donate_date[donor_key]

## check if the donor is a repeat donor and output the information if the current
## record from a repeat donor newer than the oldest record for this donor
def handle_repeat_donor(info,donor_key,percentile,output_file,newer_than_oldest_record):

    ## if it is the first time donor, store the info into the first time donor
    ## dictionary
    if donor_freq_dict[donor_key] == 1:
        add_to_donor_first_time_info(donor_key,info)

    ## if it is the second time donor (repeat donor), delete the info in the first
    ## time dictionary and pass the information into cmted dictionary
    else:
        if donor_freq_dict[donor_key] == 2:
            repeat_donor_info = pop_donor_first_time_info(donor_key)
            add_to_cmte_dict(repeat_donor_info)
        add_to_cmte_dict(info)

        ## only write into the file if the current record newer than the oldest
        ## one in record in case the data is list out of order
        if(newer_than_oldest_record):
            output_info = get_output_info(info,percentile)
            output_recipient_info(output_info,output_file)

## get the percentile from the file
def get_percentile():
    percentile_file = open(input_percentile_location)
    percentile = int(percentile_file.read())
    percentile_file.close()
    return percentile

## main function
if __name__ == "__main__":

    ## get the percentile specify in the file
    percentile = get_percentile()

    ## open both the input and output file
    output_file = open(output_location,"w")
    itcont_file = open(input_itcont_location,"r")

    ## read each line in the file and extract the needed information
    while True:
        line = itcont_file.readline()
        if not line:
            break
        info = extract_donation_info(line)
        if not info:
            continue
        donor_key = (info["name"],info["zip_code"])

        ## everytime extract a record, update the frequency of the donor
        add_donor_freq_dict(donor_key)

        ## check if the current record newer than oldest record for this donor
        newer_than_oldest_record = check_if_newer_than_oldest_record(info,donor_key)

        ##update the donor oldest record
        update_donor_oldest_donate_date(info)

        ## check if the donor is repeat donor and output the information if need.
        handle_repeat_donor(info,donor_key,percentile,output_file,newer_than_oldest_record)

    ## close both the input and output file    
    itcont_file.close()
    output_file.close()
