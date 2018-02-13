Program Over View:
  The program used for identify the repeat donor and output the contribution information of each recipient,zipcode and year.
  The program's platform is python 3
 
 Program Detail:
  1. The program use 4 dictionary to store the information:
      a. cmte_id_dict: Store the contribution information per recipient, zipcode and year. The key is cmte_id, value is  
                       another dictionary whose key is name and zipcode and value is transaction amount list. And the list will 
                       be sort everytime a new value is added, which is useful to caluclate the percentile.
                       
      b. donor_freq_dict: Store the frequency of each donor, the key is name and zipcode, and the value is the frequency. The 
                          frequency of each donor will increase whenever a record of donor is found and the record is valid.
                          
      c. donor_first_time_info: The donor cannot be identified as repeat donor untile system encouter it second time, so every
                                donor has "potenial" to be a repeat donor. The dictionary key is name and zipcode and value is 
                                another dictionary that store all other information of the current record.
                                
      d. donor_oldest_donate_date: while the data date is listed out of order, it is important to record the oldest time the  
                                   donor make a donation. The program always store the donor infomration appear twice in data,
                                   but only output the information if current record is newer than the oldest record because the
                                   requirement is output the information "so far in the calender year". Eg. if same donor appear
                                   twice, first data is 2016, and second data is 01/25/2015, then in 01/25/2015, the donor has
                                   not been identified as repeat donor yet because he does not make any donation before
                                   01/25/2015.
                                   
                                   
  2. Data Structure:
     Using dictionary to store the information will make the program more efficient because the pragram included many data accessing, dictionary will be more efficent than any other structure (eg. array, list, linked list, tree)
  
  3. Error handling:
     if the data is invalid, the program will continue to the next line of data without interrupting the program running( using try...except structure). if the percentile is invalid, it will write the error message into the file and exit the program.
     

                                 
                                  
