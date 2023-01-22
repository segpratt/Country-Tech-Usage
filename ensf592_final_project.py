
# based of a countries region, sub-region, internet usage and number of cellphones

import pandas as pd
import matplotlib.pyplot as plt


def user_input_validation(alldata):
    """ Asks user for a UN-Sub-Region and if they want to analyze cellphone or internet data, 
    validates inputs and outputs the dataframe based on the user inputs 
    """
    #while loop to get a valid sub_region name if the input is not in the UN Sub-Region data it will raise a value error 
    while True:
        try:
            sub_region = input("Please enter a sub-region: ")
            if sub_region not in alldata.index.get_level_values('UN Sub-Region'):
                raise ValueError
            else:
                break
        except ValueError:
            print ("You must enter a valid UN sub-region name.")

    #while loop to get a valid cellphone or internet name, if the input is not total cellphones' or 'internet usage per population percentage'it will raise a value error 
    while True:
        try:
            cellphone_or_internet = input("\nPlease enter 'total cellphones' or 'internet usage per population percentage' to see the data that corresponds to it: ")
            if cellphone_or_internet not in alldata.columns or cellphone_or_internet.isdigit():
                raise ValueError
            else:
                break
        except ValueError:
            print ("You must enter 'total cellphones' or 'internet usage per population percentage'.")

    #print sub array of selected data
    user_subarray = alldata.loc[(slice(None),[sub_region]),[cellphone_or_internet]]
    print(f"\nThe year by year data for {sub_region} on {cellphone_or_internet} usage is \n \n {user_subarray} ")

def pivot_table_and_plots(alldata, cellphone_or_internet):
    """ This function is used to create plots that show the maximum cellphone data or internet data 
    for each year based on the UN Region 
    """
    # stacks the years next to the country index
    max_of_data = alldata.stack(level=1)
    # removes the indexes and makes them columns 
    max_of_data.reset_index(inplace=True)
    # drops the mean internet mean column and the cellphone mean column 
    max_of_data.drop('Cellphone Mean', inplace=True, axis=1)
    max_of_data.drop('Internet Mean', inplace=True, axis=1)
    # renames the level_3 column to Year 
    max_of_data = max_of_data.rename(columns={"level_3":"Year"})
    # creates a pivot table, based on the index of UN Region, columns year, values is either the cellphone or internet data and uses aggfunct to calculate the max for each UN Region 
    max_of_data = max_of_data.pivot_table(index=('UN Region'),columns=('Year'), values= cellphone_or_internet, aggfunc='max')
    print(f"\nPivot table showing the max {cellphone_or_internet} per year based on UN Region \n \n {max_of_data}")
    max_of_data = max_of_data.T.plot(kind='bar', ylabel="max of " + cellphone_or_internet, xlabel = 'years', title = "max of " + cellphone_or_internet + " vs. years")
    plt.savefig(f"max of {cellphone_or_internet} vs. years.png")


def main():
    # Stage 1 Dataset Selection and Stage 2 Dataframe Creation
    #import and mung UN Code data, set the index to UN Region -> UN Sub-Region -> Country
    UN_codes_data = pd.read_excel('./Country Tech Use/UN Codes.xlsx')
    UN_codes_data.set_index(['UN Region','UN Sub-Region','Country'], inplace=True, drop=True, append=True)
    UN_codes_data.reset_index([0], inplace=True,drop=True)
    UN_codes_data.sort_index(inplace=True)
    
    #import and mung total_cellphones_by_country data set the index as country and rename country to Country to match the UN codes dataset
    total_cellphones_by_country_data = pd.read_excel('./Country Tech Use/total_cell_phones_by_country.xlsx')
    total_cellphones_by_country_data.set_index(['country'], inplace=True, drop=True, append=True)
    total_cellphones_by_country_data.reset_index([0], inplace=True,drop=True)
    total_cellphones_by_country_data.sort_index(inplace=True)
    total_cellphones_by_country_data.index.rename('Country', inplace=True)

    #merge UN Code and cellphone data by Country
    total_cellphones_by_country_data = pd.merge(UN_codes_data, total_cellphones_by_country_data, left_index=True, right_index=True)
    
    #import and mung internet_per_pop data, set the index as country and rename country to Country to match the UN codes dataset 
    percentage_population_internet_users_data = pd.read_excel('./Country Tech Use/percentage_population_internet_users.xlsx')
    percentage_population_internet_users_data.set_index(['country'], inplace=True, drop=True, append=True)
    percentage_population_internet_users_data.reset_index([0], inplace=True,drop=True)
    percentage_population_internet_users_data.sort_index(inplace=True)
    percentage_population_internet_users_data.index.rename('Country', inplace=True)

    #merge UN Codes data and internet data by Country
    percentage_population_internet_users_data = pd.merge(UN_codes_data, percentage_population_internet_users_data, left_index=True, right_index=True)

    #merge Internet data with Cellphone data based on country
    alldata = pd.merge(total_cellphones_by_country_data, percentage_population_internet_users_data, left_index=True, right_index=True)
    # Sort data
    alldata = alldata[(sorted(alldata.columns))]
    #remove years from 1975 - 1989 with no data
    alldata.drop(alldata.loc[:, '1975_x':'1989_y'].columns, inplace = True, axis=1 )
    #replace all Nan values with 0
    alldata = alldata.fillna(0)
    #split columns to make a multi-index column
    alldata.columns = alldata.columns.str.split('_', expand=True)
    #swap levels of years and media type
    alldata.columns = alldata.columns.swaplevel(1,0)
    #rename columns for cellphone and internet
    alldata = alldata.rename(columns={'x': 'total cellphones', 'y': 'internet usage per population percentage' })

    # Stage 3 User Input 
    # user input
    print("User validation \n")
    user_input_validation(alldata)

    # Step 4 Data Aggregation
    print("\nYear by year stats of internet and cellphone use globally \n")
    print(alldata.describe())

    # calculates the mean for each country based on internet usage and total cellphones for all the years
    mean_data = alldata.groupby(axis =1,level=0).mean()
    # creates a variable for the total cellphones column in the dataframe
    cellphone_data = mean_data.loc[:,['total cellphones']]
    # creates a variable for the internet usage column in the dataframe
    internet_data = mean_data.loc[:,['internet usage per population percentage']]

    # adds two columns to the dataset one for cellphone mean and one for internet mean 
    alldata['Cellphone Mean'] = cellphone_data
    alldata['Internet Mean'] = internet_data
    
    # print out all data with the 2 added columns
    print("\nThe year by year data for cellphones and internet use globally including added mean value columns for each country\n")
    print(alldata)
    # masking operation 
    # drops the index UN Sub-Region and UN Region from the data frame
    country_data = alldata.droplevel(0, axis = 0)
    country_data = country_data.droplevel(0, axis=0)
    # uses an aggregate function for a subset of the data to calculate the median of the cellphone mean for all the countries
    cellphone_median = alldata['Cellphone Mean'].aggregate('median')
    print('\nCountries that have a cellphone mean greater than the cellphone median for all countries\n')
    # uses a masking operation to check whether or not the cellphone mean in the country is greater than the median and prints the countries that are
    print(country_data[country_data['Cellphone Mean'] > cellphone_median]['Cellphone Mean'])
    # uses an aggregate function to for a subset of the data to calculate the median of the internet mean for all the countries
    internet_median = alldata['Internet Mean'].aggregate('median')
    print('\nCountries that have a internet mean greater than the internet median for all countries\n')
    # uses a masking operation to check whether or not the internet mean in the country is greater than the median and prints the countries that are
    print(country_data[country_data['Internet Mean'] > internet_median]['Internet Mean'])

    # Plots that show the maximum cellphone data or internet data for each year based on the UN Region  
    pivot_table_and_plots(alldata, 'internet usage per population percentage')
    pivot_table_and_plots(alldata, 'total cellphones')
    plt.show()

    #export the indexed dataframe to excel
    alldata.to_excel("Internet-Cellphone Dataframe.xlsx", index= True)


if __name__ == '__main__':
    main()

























