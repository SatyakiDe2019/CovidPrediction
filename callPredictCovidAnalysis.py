##############################################
#### Written By: SATYAKI DE               ####
#### Written On: 26-Jul-2021              ####
#### Modified On 26-Jul-2021              ####
####                                      ####
#### Objective: Calling multiple API's    ####
#### that including Prophet-API developed ####
#### by Facebook for future prediction of ####
#### Covid-19 situations in upcoming days ####
#### for world's major hotspots.          ####
##############################################

import json

import clsCovidAPI as ca
from clsConfig import clsConfig as cf
import datetime
import logging
import clsL as cl

import clsForecast as f

from prophet import Prophet

from prophet.plot import plot_plotly, plot_components_plotly

import matplotlib.pyplot as plt
import pandas as p

# Disbling Warning
def warn(*args, **kwargs):
    pass

import warnings
warnings.warn = warn

# Initiating Log class
l = cl.clsL()

# Helper Function that removes underscores
def countryDet(inputCD):
    try:
        countryCD = inputCD

        if str(countryCD) == 'DE':
            cntCD = 'Germany'
        elif str(countryCD) == 'BR':
            cntCD = 'Brazil'
        elif str(countryCD) == 'GB':
            cntCD = 'United Kingdom'
        elif str(countryCD) == 'US':
            cntCD = 'United States'
        elif str(countryCD) == 'IN':
            cntCD = 'India'
        elif str(countryCD) == 'CA':
            cntCD = 'Canada'
        elif str(countryCD) == 'ID':
            cntCD = 'Indonesia'
        else:
            cntCD = 'N/A'

        return cntCD
    except:
        cntCD = 'N/A'

        return cntCD

def plot_picture(inputDF, debug_ind, var, countryCD, stat):
    try:
        iDF = inputDF

        # Lowercase the column names
        iDF.columns = [c.lower() for c in iDF.columns]
        # Determine which is Y axis
        y_col = [c for c in iDF.columns if c.startswith('y')][0]
        # Determine which is X axis
        x_col = [c for c in iDF.columns if c.startswith('ds')][0]

        # Data Conversion
        iDF['y'] = iDF[y_col].astype('float')
        iDF['ds'] = iDF[x_col].astype('datetime64[ns]')

        # Forecast calculations
        # Decreasing the changepoint_prior_scale to 0.001 to make the trend less flexible
        m = Prophet(n_changepoints=20, yearly_seasonality=True, changepoint_prior_scale=0.001)
        m.fit(iDF)

        forecastDF = m.make_future_dataframe(periods=365)

        forecastDF = m.predict(forecastDF)

        l.logr('15.forecastDF_' + var + '_' + countryCD + '.csv', debug_ind, forecastDF, 'log')

        df_M = forecastDF[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

        l.logr('16.df_M_' + var + '_' + countryCD + '.csv', debug_ind, df_M, 'log')

        #m.plot_components(df_M)
        # Getting Full Country Name
        cntCD = countryDet(countryCD)

        # Draw forecast results
        lbl = str(cntCD) + ' - Covid - ' + stat
        m.plot(df_M, xlabel = 'Date', ylabel = lbl)

        # Combine all graps in the same page
        plt.title(f'Covid Forecasting')
        plt.title(lbl)
        plt.ylabel('Millions')
        plt.show()

        return 0

    except Exception as e:
        x = str(e)
        print(x)

        return 1

def countrySpecificDF(counryDF, val):
    try:
        countryName = val
        df = counryDF

        df_lkpFile = df[(df['CountryCode'] == val)]

        return df_lkpFile
    except:
        df = p.DataFrame()

        return df

def main():
    try:
        var1 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print('*' *60)
        DInd = 'Y'
        NC = 'New Confirmed'
        ND = 'New Dead'
        SM = 'data process Successful!'
        FM = 'data process Failure!'

        print("Calling the custom Package for large file splitting..")
        print('Start Time: ' + str(var1))

        countryList = str(cf.conf['coList']).split(',')

        # Initiating Log Class
        general_log_path = str(cf.conf['LOG_PATH'])

        # Enabling Logging Info
        logging.basicConfig(filename=general_log_path + 'CovidAPI.log', level=logging.INFO)

        # Create the instance of the Covid API Class
        x1 = ca.clsCovidAPI()

        # Let's pass this to our map section
        retDF = x1.searchQry(var1, DInd)

        retVal = int(retDF.shape[0])

        if retVal > 0:
            print('Successfully Covid Data Extracted from the API-source.')
        else:
            print('Something wrong with your API-source!')

        # Extracting Skeleton Data
        df = retDF[['data.code', 'date', 'deaths', 'confirmed', 'recovered', 'new_confirmed', 'new_recovered', 'new_deaths', 'active']]

        df.columns = ['CountryCode', 'ReportedDate', 'TotalReportedDead', 'TotalConfirmedCase', 'TotalRecovered', 'NewConfirmed', 'NewRecovered', 'NewDeaths', 'ActiveCaases']

        df.dropna()

        print('Returned Skeleton Data Frame: ')
        print(df)

        l.logr('5.df_' + var1 + '.csv', DInd, df, 'log')

        # Working with forecast
        # Create the instance of the Forecast API Class
        x2 = f.clsForecast()

        # Fetching each country name & then get the details
        cnt = 6

        for i in countryList:
            try:
                cntryIndiv = i.strip()

                print('Country Porcessing: ' + str(cntryIndiv))

                # Creating dataframe for each country
                # Germany Main DataFrame
                dfCountry = countrySpecificDF(df, cntryIndiv)
                l.logr(str(cnt) + '.df_' + cntryIndiv + '_' + var1 + '.csv', DInd, dfCountry, 'log')

                # Let's pass this to our map section
                retDFGenNC = x2.forecastNewConfirmed(dfCountry, DInd, var1)

                statVal = str(NC)

                a1 = plot_picture(retDFGenNC, DInd, var1, cntryIndiv, statVal)

                retDFGenNC_D = x2.forecastNewDead(dfCountry, DInd, var1)

                statVal = str(ND)

                a2 = plot_picture(retDFGenNC_D, DInd, var1, cntryIndiv, statVal)

                cntryFullName = countryDet(cntryIndiv)

                if (a1 + a2) == 0:
                    oprMsg = cntryFullName + ' ' + SM
                    print(oprMsg)
                else:
                    oprMsg = cntryFullName + ' ' + FM
                    print(oprMsg)

                # Resetting the dataframe value for the next iteration
                dfCountry = p.DataFrame()
                cntryIndiv = ''
                oprMsg = ''
                cntryFullName = ''
                a1 = 0
                a2 = 0
                statVal = ''

                cnt += 1
            except Exception as e:
                x = str(e)
                print(x)

        var2 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print('End Time: ' + str(var2))
        print('*' *60)

    except Exception as e:
        x = str(e)

if __name__ == "__main__":
    main()
