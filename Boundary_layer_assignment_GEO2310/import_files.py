import pandas as pd
import glob
import os


# This function can be imported into another script by adding
# "from import_files import importfiles"
def import_files(folder):
	prepared_file_names=glob.glob(folder+'/*.csv')
	prepared_file_names.sort() # sort files
	periodnames=[]
	first=True
	for prepared_file_name in prepared_file_names:
		print('Importing: '+prepared_file_name)
		df = pd.read_csv(prepared_file_name,index_col=0,parse_dates=True)#,index_col='DateTime')
		if first:
			output_dtset=df
			first=False
		else:
			frames=[output_dtset,df]
			output_dtset=pd.concat(frames) # concatinate files
		periodnames.append(prepared_file_name.split('/')[2].split('.')[0] )
	output_dtset = output_dtset.rename( columns={"H20_ppt": "H2O_ppt"})
	return output_dtset, periodnames  #return dataset and periodnames from the files.

