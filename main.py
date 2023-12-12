# This Python file uses the following encoding: utf-8
import sys
import os

#Qt imports
from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QListWidgetItem, QMessageBox, QProgressDialog
from PySide2.QtCore import QFile, QDate, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QDoubleValidator, QBrush, QColor, QIcon

#extra hidden import for the executable conversion
from PySide2 import QtXml
import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy

#icon on task bar
try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PySide2.QtWinExtras import QtWin
    myappid = 'dr. cat\'s stock screener'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

#pandas and numpy imports for data storage and manipulation
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np

#datetime imports for date management
from datetime import date
import datetime

#finance API imports (yahoo finance and finviz finance) for downloading stock data
import yfinance as yf
yf.pdr_override()
from finvizfinance.quote import finvizfinance

#Google trends API imports for fetching the related trending topics
from pytrends.request import TrendReq
import pytrends

#HTTP requests for the various API modules
import requests
import requests_html
import urllib.request

#unicode data inport for sanitizing some of the strings for URLs
import unicodedata

#BeautifulSoup import for reading tables from some of the websites
from bs4 import BeautifulSoup

#Main Window Class
class StockScreener(QMainWindow):
    #initialize window
    def __init__(self):
        #call initialize from QMainWindow
        super(StockScreener, self).__init__()
        #load the associated UI file
        self.load_ui()

        #Create double validator for the line edits
        validator = QDoubleValidator(-9999, 9999, 4)
        #Set validator for the price line edit
        self.ui.price.setValidator(validator)
        #Set validator for the sales line edit
        self.ui.sales.setValidator(validator)
        #Set validator for the EPS line edit
        self.ui.eps.setValidator(validator)


        ##########################################
        #Set button signals and control variables#
        ##########################################
        #buys button signal
        self.ui.buysButton.clicked.connect(self.bs_on)
        #sells button signal
        self.ui.sellsButton.clicked.connect(self.bs_off)
        #year button signal
        self.ui.yearButton.clicked.connect(self.yq_on)
        #quarter button signal
        self.ui.quarterButton.clicked.connect(self.yq_off)

        #buys/sells control variable
        self.buys_sells = None
        #year/quarter control variable
        self.year_quarter = None


        #########################
        #Set Top10 table signals#
        #########################
        #tab widget signal
        self.ui.Top10.currentChanged.connect(self.updateTop10)

        ##################################
        #Setup the tables inside each tab#
        ##################################
        ##################################
        #GSPC or S&P500 table
        #Rows and Columns (11x4)
        self.ui.GSPCTab.setRowCount(11)
        self.ui.GSPCTab.setColumnCount(4)

        #Setup the corner cell
        newItem = QTableWidgetItem(self.tr(""))
        newItem.setBackground(QColor(0, 0, 0))
        self.ui.GSPCTab.setItem(0, 0, newItem)

        #Setup the column names
        newItem = QTableWidgetItem(self.tr("Top10"))
        self.ui.GSPCTab.setItem(0, 1, newItem)
        newItem = QTableWidgetItem(self.tr("Sector"))
        self.ui.GSPCTab.setItem(0, 2, newItem)
        newItem = QTableWidgetItem(self.tr("Ticker"))
        self.ui.GSPCTab.setItem(0, 3, newItem)

        #Setup the column widths
        self.ui.GSPCTab.setColumnWidth(0, 20)
        self.ui.GSPCTab.setColumnWidth(1, 150)
        self.ui.GSPCTab.setColumnWidth(2, 100)

        ##########################################
        #DJI or Dow Jones Industrial Average table
        #Rows and Columns (11x4)
        self.ui.DJITab.setRowCount(11)
        self.ui.DJITab.setColumnCount(4)

        #Setup the corner cell
        newItem = QTableWidgetItem(self.tr(""))
        newItem.setBackground(QColor(0, 0, 0))
        self.ui.DJITab.setItem(0, 0, newItem)

        #Setup the column names
        newItem = QTableWidgetItem(self.tr("Top10"))
        self.ui.DJITab.setItem(0, 1, newItem)
        newItem = QTableWidgetItem(self.tr("Sector"))
        self.ui.DJITab.setItem(0, 2, newItem)
        newItem = QTableWidgetItem(self.tr("Ticker"))
        self.ui.DJITab.setItem(0, 3, newItem)

        #Setup the column widths
        self.ui.DJITab.setColumnWidth(0, 20)
        self.ui.DJITab.setColumnWidth(1, 150)
        self.ui.DJITab.setColumnWidth(2, 100)

        #######################################
        #IXIC or Nasdaq Composite table
        #Rows and Columns (11x4)
        self.ui.IXICTab.setRowCount(11)
        self.ui.IXICTab.setColumnCount(4)

        #Setup the corner cell
        newItem = QTableWidgetItem(self.tr(""))
        newItem.setBackground(QColor(0, 0, 0))
        self.ui.IXICTab.setItem(0, 0, newItem)

        #Setup the column names
        newItem = QTableWidgetItem(self.tr("Top10"))
        self.ui.IXICTab.setItem(0, 1, newItem)
        newItem = QTableWidgetItem(self.tr("Sector"))
        self.ui.IXICTab.setItem(0, 2, newItem)
        newItem = QTableWidgetItem(self.tr("Ticker"))
        self.ui.IXICTab.setItem(0, 3, newItem)

        #Setup the column widths
        self.ui.IXICTab.setColumnWidth(0, 20)
        self.ui.IXICTab.setColumnWidth(1, 150)
        self.ui.IXICTab.setColumnWidth(2, 100)

        ########################################
        #NYA or NYSE COMPOSITE table
        #Rows and Columns (11x4)
        self.ui.NYATab.setRowCount(11)
        self.ui.NYATab.setColumnCount(4)

        #Setup the corner cell
        newItem = QTableWidgetItem(self.tr(""))
        newItem.setBackground(QColor(0, 0, 0))
        self.ui.NYATab.setItem(0, 0, newItem)

        #Setup the column names
        newItem = QTableWidgetItem(self.tr("Top10"))
        self.ui.NYATab.setItem(0, 1, newItem)
        newItem = QTableWidgetItem(self.tr("Sector"))
        self.ui.NYATab.setItem(0, 2, newItem)
        newItem = QTableWidgetItem(self.tr("Ticker"))
        self.ui.NYATab.setItem(0, 3, newItem)

        #Setup the column widths
        self.ui.NYATab.setColumnWidth(0, 20)
        self.ui.NYATab.setColumnWidth(1, 150)
        self.ui.NYATab.setColumnWidth(2, 100)

        ########################################
        #RUT or Russell 2000 table
        #Rows and Columns (11x4)
        self.ui.RUTTab.setRowCount(11)
        self.ui.RUTTab.setColumnCount(4)

        #Setup the corner cell
        newItem = QTableWidgetItem(self.tr(""))
        newItem.setBackground(QColor(0, 0, 0))
        self.ui.RUTTab.setItem(0, 0, newItem)

        #Setup the column names
        newItem = QTableWidgetItem(self.tr("Top10"))
        self.ui.RUTTab.setItem(0, 1, newItem)
        newItem = QTableWidgetItem(self.tr("Sector"))
        self.ui.RUTTab.setItem(0, 2, newItem)
        newItem = QTableWidgetItem(self.tr("Ticker"))
        self.ui.RUTTab.setItem(0, 3, newItem)

        #Setup the column widths
        self.ui.RUTTab.setColumnWidth(0, 20)
        self.ui.RUTTab.setColumnWidth(1, 150)
        self.ui.RUTTab.setColumnWidth(2, 100)

        ###############################################################
        #connect the signals of the input fields to update the results#
        ###############################################################
        #Set the minium and maximum dates of the date edits to the limits of the downloaded data
        #Start Date
        self.ui.startDate.setMinimumDate(QDate(1986, 1, 1))
        self.ui.startDate.setMaximumDate(QDate(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day))
        #End Date
        self.ui.endDate.setMinimumDate(QDate(1986, 1, 1))
        self.ui.endDate.setMaximumDate(QDate(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day))

        #Set the date to the minimum for the start date and maximum for the end date
        #Start Date
        self.ui.startDate.setDate(QDate(1986, 1, 1))
        self.ui.startDate.dateChanged.connect(self.filterResults)

        #End Date
        self.ui.endDate.setDate(QDate(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day))
        self.ui.endDate.dateChanged.connect(self.filterResults)

        #price line edit signal
        self.ui.price.textEdited.connect(self.filterResults)
        #sales line edit signal
        self.ui.sales.textEdited.connect(self.filterResults)
        #EPS line edit signal
        self.ui.eps.textEdited.connect(self.filterResults)

        ####################################################################
        #Connect the signals of the page buttons to update the results list#
        ####################################################################
        #Next Page
        self.ui.nextPage.clicked.connect(self.updateResults)
        #Previous Page
        self.ui.prevPage.clicked.connect(self.updateResults2)

        #Number of results per page
        self.n = 20000 #chunk row size
        #Execute a results filter to update the list and various elements
        self.filterResults()


    #load the UI file
    def load_ui(self):
        #Qt UI loader
        loader = QUiLoader()
        #path to the UI file
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        #create the file object and open it
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        #load the ui to the self.ui variable
        self.ui = loader.load(ui_file, self)
        #close the UI file
        ui_file.close()

    ##############################
    #Insider Transactions Buttons#
    ##############################
    #execute when sells button is clicked
    def bs_off(self):
        #if the current state of buys/sells is true (buys) or none (neither buys or sells)
        if self.buys_sells or self.buys_sells is None:
            #set buys_sells to false (sells)
            self.buys_sells = False
        else:
            #set buys_sells to none (neither buys or sells)
            self.buys_sells = None
        #update the button colors
        self.update_button_state()
        #filter the insider transactions results according to the selection
        self.filterInsiders()

    #execute when buys button is clicked
    def bs_on(self):
        #if the current state of buys/sells is true (buys)
        if self.buys_sells:
            #set buys_sells to none (neither buys or sells)
            self.buys_sells = None
        else:
            #set buys_sells to true (buys)
            self.buys_sells = True
        #update the button colors
        self.update_button_state()
        #filter the insider transactions results according to the selection
        self.filterInsiders()

    #execute when quarter button is clicked
    def yq_off(self):
        #if the current state of year/quarter is true (year) or none (neither year or quarter)
        if self.year_quarter or self.year_quarter is None:
            #set year_quarter to false (quarter)
            self.year_quarter = False
        else:
            #set year_quarter to none (neither year or quarter)
            self.year_quarter = None
        #update the button colors
        self.update_button_state()
        #filter the insider transactions results according to the selection
        self.filterInsiders()

    #execute when year button is clicked
    def yq_on(self):
        #if the current state of year/quarter is true (year)
        if self.year_quarter:
            #set year_quarter to none (neither year or quarter)
            self.year_quarter = None
        else:
            #set year_quarter to true (year)
            self.year_quarter = True
        #update the button colors
        self.update_button_state()
        #filter the insider transactions results according to the selection
        self.filterInsiders()


    #update the insider transactions buttons states
    def update_button_state(self):
        #if the buys button is active
        if self.buys_sells and not self.buys_sells is None:
            #change buttons colors
            self.ui.buysButton.setStyleSheet("background-color: #f0932a; color: #fff;")
            self.ui.sellsButton.setStyleSheet("background-color: none; color: none;")
        #if the sells button is active
        elif not self.buys_sells is None:
            #change buttons colors
            self.ui.buysButton.setStyleSheet("background-color: none; color: none;")
            self.ui.sellsButton.setStyleSheet("background-color: #2a91f0; color: #fff;")
        #if neither are active
        else:
            #reset everything
            self.ui.buysButton.setStyleSheet("background-color: none; color: none;")
            self.ui.sellsButton.setStyleSheet("background-color: none; color: none;")
            self.buys_sells = None

        #if the year button is active
        if self.year_quarter and not self.year_quarter is None:
            #change buttons colors
            self.ui.yearButton.setStyleSheet("background-color: #ff87ca; color: #fff;")
            self.ui.quarterButton.setStyleSheet("background-color: none; color: none;")
        #if the quarter button is active
        elif not self.year_quarter is None:
            #change buttons colors
            self.ui.yearButton.setStyleSheet("background-color: none; color: none;")
            self.ui.quarterButton.setStyleSheet("background-color: #70f02a; color: #fff;")
        #if neither are active
        else:
            #reset everything
            self.ui.yearButton.setStyleSheet("background-color: none; color: none;")
            self.ui.quarterButton.setStyleSheet("background-color: none; color: none;")
            self.year_quarter = None


    ############
    #Top10 Tabs#
    ############
    #update the top10 of the active market tab
    def updateTop10(self):
        #get the current active tab index
        activeMarket = self.ui.Top10.currentIndex()
        #if the first tab is active
        if activeMarket == 0:
            #GSPC
            #get the top10 related topics in the US for these keywords
            result = get_Top10_searches_US(["GSPC", "S&P500", "^GSPC"])

            #iterate through the results
            for index, row in result.iterrows():
                #set the line in the top10 table to the respective results fields
                newItem = QTableWidgetItem(self.tr("%d" % (index + 1)))
                self.ui.GSPCTab.setItem(index + 1, 0, newItem)

                ticker = ""
                tickerF = False
                #try to match the topic with a ticker in the SP500 ticker list
                for item in SP500:
                    for s in row["topic_name"].split():
                        if s.replace(".", " ").replace(",", " ").strip() in item[1] and not("inc" in s.replace(".", " ").replace(",", " ").strip().lower() or "company" in s.replace(".", " ").replace(",", " ").strip().lower()):
                            ticker = item[0]
                            tickerF = True
                            break
                    if tickerF:
                        break
                    ticker = "N/A"

                newItem = QTableWidgetItem(self.tr(ticker))
                self.ui.GSPCTab.setItem(index + 1, 3, newItem)

                newItem = QTableWidgetItem(self.tr(row["topic_name"]))
                self.ui.GSPCTab.setItem(index + 1, 1, newItem)
                newItem = QTableWidgetItem(self.tr(row["topic_type"]))
                self.ui.GSPCTab.setItem(index + 1, 2, newItem)

        #same as previous, but for the second tab
        elif activeMarket == 1:
            #DJI
            result = get_Top10_searches_US(["Dow Jones Industrial Average", "^DJI"])
            #do some extra filtering, because DJI is also a drone company

            result = result.loc[(result['topic_type'] != "Aircraft type") & (result['topic_name'] != "NASDAQ") & (result['topic_name'] != "nasdaq")].sort_values(by=['value'], ascending=False).reset_index().drop(['index'], axis=1)

            for index, row in result.iterrows():
                newItem = QTableWidgetItem(self.tr("%d" % (index + 1)))
                self.ui.DJITab.setItem(index + 1, 0, newItem)

                ticker = ""
                tickerF = False
                for item in DJI:
                    for s in row["topic_name"].split():
                        if s.replace(".", " ").replace(",", " ").strip() in item[1] and not("inc" in s.replace(".", " ").replace(",", " ").strip().lower() or "company" in s.replace(".", " ").replace(",", " ").strip().lower()):
                            ticker = item[0]
                            tickerF = True
                            break
                    if tickerF:
                        break
                    ticker = "N/A"

                newItem = QTableWidgetItem(self.tr(ticker))
                self.ui.DJITab.setItem(index + 1, 3, newItem)

                newItem = QTableWidgetItem(self.tr(row["topic_name"]))
                self.ui.DJITab.setItem(index + 1, 1, newItem)
                newItem = QTableWidgetItem(self.tr(row["topic_type"]))
                self.ui.DJITab.setItem(index + 1, 2, newItem)

        #same as previous, but for the third tab
        elif activeMarket == 2:
            #IXIC
            result = get_Top10_searches_US(["IXIC", "Nasdaq Composite", "^IXIC"])
            for index, row in result.iterrows():
                newItem = QTableWidgetItem(self.tr("%d" % (index + 1)))
                self.ui.IXICTab.setItem(index + 1, 0, newItem)

                ticker = ""
                tickerF = False
                for item in IXIC:
                    for s in row["topic_name"].split():
                        if s.replace(".", " ").replace(",", " ").strip() in item[1] and not("inc" in s.replace(".", " ").replace(",", " ").strip().lower() or "company" in s.replace(".", " ").replace(",", " ").strip().lower()):
                            ticker = item[0]
                            tickerF = True
                            break
                    if tickerF:
                        break
                    ticker = "N/A"

                newItem = QTableWidgetItem(self.tr(ticker))
                self.ui.IXICTab.setItem(index + 1, 3, newItem)

                newItem = QTableWidgetItem(self.tr(row["topic_name"]))
                self.ui.IXICTab.setItem(index + 1, 1, newItem)
                newItem = QTableWidgetItem(self.tr(row["topic_type"]))
                self.ui.IXICTab.setItem(index + 1, 2, newItem)

        #same as previous, but for the fourth tab
        elif activeMarket == 3:
            #NYA
            result = get_Top10_searches_US(["NYSE Stocks", "NYSE Composite"])
            for index, row in result.iterrows():
                newItem = QTableWidgetItem(self.tr("%d" % (index + 1)))
                self.ui.NYATab.setItem(index + 1, 0, newItem)

                ticker = ""
                tickerF = False
                for item in NYA:
                    for s in row["topic_name"].split():
                        if s.replace(".", " ").replace(",", " ").strip() in item[1] and not("inc" in s.replace(".", " ").replace(",", " ").strip().lower() or "company" in s.replace(".", " ").replace(",", " ").strip().lower()):
                            ticker = item[0]
                            tickerF = True
                            break
                    if tickerF:
                        break
                    ticker = "N/A"

                newItem = QTableWidgetItem(self.tr(ticker))
                self.ui.NYATab.setItem(index + 1, 3, newItem)

                newItem = QTableWidgetItem(self.tr(row["topic_name"]))
                self.ui.NYATab.setItem(index + 1, 1, newItem)
                newItem = QTableWidgetItem(self.tr(row["topic_type"]))
                self.ui.NYATab.setItem(index + 1, 2, newItem)

        #same as previous, but for the fifth tab
        elif activeMarket == 4:
            #RUT
            result = get_Top10_searches_US(["Russell 2000"])
            for index, row in result.iterrows():
                newItem = QTableWidgetItem(self.tr("%d" % (index + 1)))
                self.ui.RUTTab.setItem(index + 1, 0, newItem)

                ticker = ""
                tickerF = False
                for item in Russell2000:
                    for s in row["topic_name"].split():
                        if s.replace(".", " ").replace(",", " ").strip() in item[1] and not("inc" in s.replace(".", " ").replace(",", " ").strip().lower() or "company" in s.replace(".", " ").replace(",", " ").strip().lower()):
                            ticker = item[0]
                            tickerF = True
                            break
                    if tickerF:
                        break
                    ticker = "N/A"

                newItem = QTableWidgetItem(self.tr(ticker))
                self.ui.RUTTab.setItem(index + 1, 3, newItem)

                newItem = QTableWidgetItem(self.tr(row["topic_name"]))
                self.ui.RUTTab.setItem(index + 1, 1, newItem)
                newItem = QTableWidgetItem(self.tr(row["topic_type"]))
                self.ui.RUTTab.setItem(index + 1, 2, newItem)



    #filter the results list according to the selected parameters
    def filterResults(self):
        #get the start date from the start date edit
        start = datetime.datetime(self.ui.startDate.date().year(),self.ui.startDate.date().month(),self.ui.startDate.date().day()).strftime("%Y-%m-%d")
        #get the end date from the end date edit
        end = datetime.datetime(self.ui.endDate.date().year(),self.ui.endDate.date().month(),self.ui.endDate.date().day()).strftime("%Y-%m-%d")

        #apply the date filter to the stocks list
        filter_stocks = stocks_final.loc[stocks_final.index.to_series().between(start, end)]

        #if the text in the price line edit is not empty then filter by the price as well
        if not self.ui.price.text() is "":
            #compare the price in the input to the price in the stocks list
            price_filter = (round(filter_stocks["Close_change"], 4) * 100 == float(self.ui.price.text()))
            #filter the stocks list by this comparison
            filter_stocks = filter_stocks.loc[price_filter]

        #if the text in the sales line edit is not empty then filter by the sales as well
        if not self.ui.sales.text() in "":
            #compare the sales in the input to the sales in the stocks list
            quarter_filter = (round(filter_stocks["Close_y"], 4) * 100 == float(self.ui.sales.text()))
            #filter the stocks list by this comparison
            filter_stocks = filter_stocks.loc[quarter_filter]

        #if the text in the eps line edit is not empty then filter by the eps as well
        if not self.ui.eps.text() in "":
            #merge the stocks list with the eps list for each ticker and store in a temporary variable
            tmp = pd.merge(filter_stocks, full_tickersEPS, on='Name', how='left').set_index(filter_stocks.index)
            #compare the eps in the input to the eps in the temporary list
            eps_filter = (tmp["EPS"] == str(round((float(self.ui.eps.text()) / 100), 4)))
            #filter the stocks list by this comparison
            filter_stocks = filter_stocks.loc[eps_filter]

        #split the filtered stocks by blocks of length self.n (20000 by default) and store in a final variable for printing
        self.list_df = [filter_stocks[i:i+self.n] for i in range(0,filter_stocks.shape[0],self.n)]

        #calculate the number of total pages for the final filtered stocks
        self.totalPages = int(len(filter_stocks.index) / self.n) + 1
        #set the page to -1 to print the first page
        self.page = -1
        #update the results in the GUI
        self.updateResults()


    #filter the insiders list according to the selected parameters
    def filterInsiders(self):
        #if either year or quarter is selected
        if not self.year_quarter is None:
            #if the year is selected then do no filtering because the full data is for the last year
            if self.year_quarter:
                filter_stocks = insider_final
            #if the quarter is selected filter the data up to the last 3 months
            else:
                #last quarter (todays month - 3)
                month = datetime.date.today().month - 3
                #check if the month is less than 0 after subtracting
                if month <= 0:
                    #set year to previous year
                    year = datetime.date.today().year - 1
                    #sum 12 to month
                    month += 12
                else:
                    #if the month is still > 0 then leave the year the same
                    year = datetime.date.today().year

                #setup the start and end dates acording to todays date and the calculated month and year
                start = datetime.datetime(year, month, datetime.date.today().day).strftime("%Y-%m-%d")
                end = datetime.datetime(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day).strftime("%Y-%m-%d")

                #filter the insider data by the dates
                filter_stocks = insider_final.loc[insider_final.Date.between(start, end)]
        else:
            #if neither are selected then do no filtering
            filter_stocks = insider_final

        #if either buys or sells are selected
        if not self.buys_sells is None:
            #if buys is selected
            if self.buys_sells:
                #comparison by the transaction type
                buys_filter = (filter_stocks["Transaction"] == "Buy")
                #filter data by this comparison
                filter_stocks = filter_stocks.loc[buys_filter]
            else:
                #comparison by the transaction type
                sale_filter = (filter_stocks["Transaction"] == "Sale")
                #filter data by this comparison
                filter_stocks = filter_stocks.loc[sale_filter]

        #if neither year or quarter or buys or sells are selected then go to the regular filter results and exit this function
        if self.year_quarter is None and self.buys_sells is None:
            self.filterResults()
            return

        #split the filtered insider information by blocks of self.n length and store in the self.list_df variable for printing
        self.list_df = [filter_stocks[i:i+self.n] for i in range(0,filter_stocks.shape[0],self.n)]

        #calculate the number of pages
        self.totalPages = int(len(filter_stocks.index) / self.n) + 1
        #set the page to -1 to print the first page
        self.page = -1
        #update the list of insider information on the GUI
        self.updateInsiders()

    #go to the previous page of the results list
    def updateResults2(self):
        #subtract 2 from the page number because the page will be incremented before the update
        self.page -= 2
        #if the page number is less than -1 (before first page)
        if self.page < -1:
            #set the page number to totalPages - 2
            self.page = self.totalPages - 2
        #update the results list on the GUI
        self.updateResults()


    #go to the next page
    def updateResults(self):
        #if either year, quater, buys or sells buttons are active then go to the update insiders function and exit
        if not self.year_quarter is None or not self.buys_sells is None:
            self.updateInsiders()
            return

        #clean the previous results list information
        self.ui.resultsList.clear()

        #set the tags to the respective fields
        self.ui.Open.setText("Open")
        self.ui.High.setText("High")
        self.ui.Low.setText("Low")
        self.ui.Close.setText("Close")
        self.ui.AdjClose.setText("Adj. Close")
        self.ui.Volume.setText("Volume")

        #increment the page to be shown
        self.page += 1
        #if the page is more than the total number of pages for the filtered data then go to the first page
        if self.page >= self.totalPages:
            self.page = 0

        #if the length of the filtered results list is > 0 then print results
        if len(self.list_df) > 0:
            #iterate through the self.n block of results and print them in the list
            for i, row in self.list_df[self.page].sort_index().iterrows():
                QListWidgetItem(self.tr(str(i).split()[0] + "\t" + "{:.4f}".format(row["Open"]) + "\t" + "{:.4f}".format(row["High"]) + "\t" + "{:.4f}".format(row["Low"]) + "\t" + "{:.4f}".format(row["Close_x"]) + "\t" + "{:.5f}".format(row["Adj Close"]) + "\t" + str(row["Volume"]) + "\t" + row["Name"]), self.ui.resultsList)
        else:
            #if there are no results then print a warning
            QListWidgetItem(self.tr("No Items for the Selected Parameters"), self.ui.resultsList)

        #update the label besides the results list with the new page number
        self.ui.pageOf.setText("Page " + str(self.page + 1) + " of " + str(self.totalPages))
        #label updates require a repaint execution for some reason
        self.ui.repaint()

    #update the insider information in the GUI
    def updateInsiders(self):
        #same as the updateResults function, but with the proper formats for the insider data
        self.ui.resultsList.clear()

        self.page += 1
        if self.page >= self.totalPages:
            self.page = 0

        self.ui.Open.setText("Insider")
        self.ui.High.setText("Relationship")
        self.ui.Low.setText("Cost")
        self.ui.Close.setText("#Shares")
        self.ui.AdjClose.setText("Total Shares")
        self.ui.Volume.setText("Insider ID")

        if len(self.list_df) > 0:
            for i, row in self.list_df[self.page].sort_values(by=["Date"]).iterrows():
                if len(str(row["Insider Trading"]).strip()) > 10:
                    intr = str(row["Insider Trading"]).strip()[:10].lower()
                else:
                    intr = str(row["Insider Trading"]).strip().lower()

                if len(str(row["Relationship"]).strip()) > 10:
                    rela = str(row["Relationship"]).strip()[:10]
                else:
                    rela = str(row["Relationship"]).strip()

                QListWidgetItem(self.tr(str(row["Date"]) + "\t" + '{:<12s} \t {:<10s}'.format(intr, rela) + "\t" + "{:.2f}".format(row["Cost"]) + "\t" + str(row["#Shares"]) + "\t" + str(row["#Shares Total"]) + "\t" + str(row["Insider_id"]) + "\t" + str(row["Ticker"]).strip()), self.ui.resultsList)
        else:
            QListWidgetItem(self.tr("No Items for the Selected Parameters"), self.ui.resultsList)

        self.ui.pageOf.setText("Page " + str(self.page + 1) + " of " + str(self.totalPages))
        self.ui.repaint()





#Top 10 searches in the US for the last 3 months.
#The google API doesn's give results for last second.
#Also doesn't give good results for last hour, 4 hours, day, week and month
def get_Top10_searches_US(keywordList):
    #Create a trend object to request the google API
    pytrend = TrendReq(hl='en-US', tz=360)

    #list of topics found
    topics = []
    #run through the keywordList passed and search for the related topics
    for word in keywordList:
        #build the pytrends payload for the last 3 months in the US
        pytrend.build_payload(
        kw_list=[word],
        cat=0,
        timeframe='today 3-m',
        geo='US')
        #get the related topics and drop every column except for the topic name and type
        try:
            tmp = pytrend.related_topics()[word]["top"].drop(['formattedValue', 'link', 'topic_mid', 'hasData'], axis=1).values.tolist()
        except (KeyError, requests.exceptions.ReadTimeout):
            tmp = []
        #append to the topic list
        [topics.append(item) for item in tmp]

    #convert the topic list to dataframe
    result = pd.DataFrame(topics, columns=['value', 'topic_name', 'topic_type'])

    #remove the topics that have type of Topic (general topic) Market Index (this or other related market indexes) and Index (this or other indexes)
    result = result.loc[(result['topic_type'] != "Topic") & (result['topic_type'] != "Market index") & (result['topic_type'] != "Index")].sort_values(by=['value'], ascending=False).reset_index().drop(['index'], axis=1).head(10)

    #return the result
    return result


#variables where to store the company (index, name) pair for each market
SP500 = []
DJI = []
IXIC = []
NYA = []
Russell2000 = []

#download SP500 ticker list
def load_SP500():
    global SP500

    #Load S&P500 components from wikipedia for later searching
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        table = soup.find('table', {'class': 'wikitable sortable'})

        #Store the components in a list of pairs
        for row in table.findAll('tr')[1:]:
            symbol = "".join(ch for ch in row.findAll('td')[0].text if unicodedata.category(ch)[0]!="C")
            t = pd.read_html('https://finance.yahoo.com/quote/' + symbol + '/analysis')
            EPS_LastQ_change = (float(t[2].loc[1][-1]) - float(t[2].loc[1][-2])) / float(t[2].loc[1][-2])
            ticker = [symbol, row.findAll('td')[1].text, EPS_LastQ_change]

            SP500.append(ticker)

        SP500 = [[s1.replace('\n', ''), s2.replace('\n', ''), s3] for [s1, s2, s3] in SP500]
    except ValueError:
        pass

    #store in file for later reading
    with open("Data/SP500.csv", "w") as f:
        for pair in SP500:
            f.write(pair[0] + "," + pair[1] + "," + str(round(pair[2], 4)) + "\n")

#download DJI ticker list
def load_DJI():
    global DJI

    #Load DJI components from yahoo finance for later searching
    DJI_top30 = pd.read_html('https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI')

    #Store the components in a list of pairs
    for (s, n) in zip(DJI_top30[0]["Symbol"].tolist(), DJI_top30[0]["Company Name"].tolist()):
        t = pd.read_html('https://finance.yahoo.com/quote/' + s + '/analysis')
        EPS_LastQ_change = (float(t[2].loc[1][-1]) - float(t[2].loc[1][-2])) / float(t[2].loc[1][-2])
        DJI.append([s, n, EPS_LastQ_change])

    #store in file for later reading
    with open("Data/DJI.csv", "w") as f:
        for pair in DJI:
            f.write(pair[0] + "," + pair[1] + "," + str(round(pair[2], 4)) + "\n")

#download IXIC ticker list
def load_IXIC():
    global IXIC

    #Load IXIC components from yahoo finance for later searching
    IXIC_top30 = pd.read_html('https://finance.yahoo.com/quote/%5EIXIC/components?p=%5EIXIC')

    #Store the components in a list of pairs
    for (s, n) in zip(IXIC_top30[0]["Symbol"].tolist(), IXIC_top30[0]["Company Name"].tolist()):
        try:
            t = pd.read_html('https://finance.yahoo.com/quote/' + s + '/analysis')
            EPS_LastQ_change = (float(t[2].loc[1][-1]) - float(t[2].loc[1][-2])) / float(t[2].loc[1][-2])
        except ValueError:
            EPS_LastQ_change = 0

        IXIC.append([s, n, EPS_LastQ_change])

    #store in file for later reading
    with open("Data/IXIC.csv", "w") as f:
        for pair in IXIC:
            f.write(pair[0] + "," + pair[1] + "," + str(round(pair[2], 4)) + "\n")

#download NYA ticker list
def load_NYA():
    global NYA

    #Load NYA components from yahoo finance for later searching
    NYA_top30 = pd.read_html('https://finance.yahoo.com/quote/%5ENYA/components?p=%5ENYA')

    #Store the components in a list of pairs
    for (s, n) in zip(NYA_top30[0]["Symbol"].tolist(), NYA_top30[0]["Company Name"].tolist()):
        try:
            t = pd.read_html('https://finance.yahoo.com/quote/' + s + '/analysis')
            try:
                EPS_LastQ_change = (float(t[2].loc[1][-1]) - float(t[2].loc[1][-2])) / float(t[2].loc[1][-2])
            except IndexError:
                EPS_LastQ_change = 0
        except ValueError:
            EPS_LastQ_change = 0

        NYA.append([s, n, EPS_LastQ_change])

    #store in file for later reading
    with open("Data/NYA.csv", "w") as f:
        for pair in NYA:
            f.write(pair[0] + "," + pair[1] + "," + str(round(pair[2], 4)) + "\n")

#download RUT ticker list
def load_Russell2000():
    global Russell2000

    #Load Russell2000 components from https://money.cnn.com/data/markets/russell/ for later searching
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

    #Read from the website. The third table is the one we are looking for
    source=requests.get("https://money.cnn.com/data/markets/russell/?%3Forder=d&iid=ob_article_footer&page=1", headers=headers).text
    Russell = pd.read_html(source)[3]["Company"]

    for item in Russell:
        t = pd.read_html('https://finance.yahoo.com/quote/' + item.split()[0] + '/analysis')
        try:
            EPS_LastQ_change = (float(t[2].loc[1][-1]) - float(t[2].loc[1][-2])) / float(t[2].loc[1][-2])
        except ZeroDivisionError:
            EPS_LastQ_change = float(t[2].loc[1][-1])
        except IndexError:
            EPS_LastQ_change = 0

        Russell2000.append([item.split()[0], " ".join(item.split()[1:]), EPS_LastQ_change])

    #This website splits the indexes in 74 pages of the table. page 1 has already been loaded
    for i in range(2, 75):
        source=requests.get("https://money.cnn.com/data/markets/russell/?%3Forder=d&iid=ob_article_footer&page=" + str(i), headers=headers).text
        tmp = pd.read_html(source)[3]["Company"]
        for item in tmp:
            try:
                t = pd.read_html('https://finance.yahoo.com/quote/' + item.split()[0] + '/analysis')
                try:
                    EPS_LastQ_change = (float(t[2].loc[1][-1]) - float(t[2].loc[1][-2])) / float(t[2].loc[1][-2])
                except ZeroDivisionError:
                    EPS_LastQ_change = float(t[2].loc[1][-1])
                except IndexError:
                    EPS_LastQ_change = 0
            except (ValueError, urllib.error.HTTPError):
                EPS_LastQ_change = 0

            Russell2000.append([item.split()[0], " ".join(item.split()[1:]), EPS_LastQ_change])


    #store in file for later reading
    with open("Data/Russell2000.csv", "w") as f:
        for pair in Russell2000:
            f.write(pair[0] + "," + pair[1] + "," + str(round(pair[2], 4)) + "\n")


#read the ticker information from file
def read_Pairs(index):
    with open("Data/" + index + ".csv", "r") as f:
        tmp = f.read().splitlines()
        tmp = [[pair.split(",")[0], pair.split(",")[1], float(pair.split(",")[-1])] for pair in tmp]

    return tmp

#read the stocks information from file
def read_Stocks(index):
    return pd.read_csv("Data/" + index + "_stocks.csv")

#read the insider information from file
def read_Insider(index):
    return pd.read_csv("Data/" + index + "_insider.csv")



#variables to store the read stock information for each market
SP500_stocks = pd.DataFrame()
DJI_stocks = pd.DataFrame()
IXIC_stocks = pd.DataFrame()
NYA_stocks = pd.DataFrame()
Russell2000_stocks = pd.DataFrame()

#download the stock information for each market
def load_SP500_stocks(start, end):
    # create empty dataframe
    global SP500_stocks

    tmp_stocks = pd.DataFrame()

    # iterate over each symbol
    for (i, name, _) in SP500:
        # print the symbol which is being downloaded
        #print( str(h) + str(' : ') + i, sep=',', end=',', flush=True)
        try:
            # download the stock price
            stock = []
            stock = yf.download(i,start=start, end=end, progress=False)

            # append the individual stock prices
            if len(stock) == 0:
                None
            else:
                stock['Name']=i
                tmp_stocks = tmp_stocks.append(stock,sort=False)
        except Exception:
            None

    tickers = tmp_stocks.Name.unique()

    for tik in tickers:
        tmp = tmp_stocks[tmp_stocks["Name"] == tik].sort_index()
        tmp['Close_change'] = tmp['Close'].pct_change()
        tmp["year"] = tmp.index.year
        tmp["Q"] = tmp.index.quarter
        tmp = tmp.merge(tmp.groupby(["year", "Q"])["Close"].sum().pct_change(), left_on = ["year", "Q"], right_index = True)

        SP500_stocks = SP500_stocks.append(tmp)

    SP500_stocks.to_csv("Data/SP500_stocks.csv")

def load_DJI_stocks(start, end):
    # create empty dataframe
    global DJI_stocks

    tmp_stocks = pd.DataFrame()

    # iterate over each symbol
    for (i, name, _) in DJI:
        # print the symbol which is being downloaded
        #print( str(h) + str(' : ') + i, sep=',', end=',', flush=True)
        try:
            # download the stock price
            stock = []
            stock = yf.download(i,start=start, end=end, progress=False)

            # append the individual stock prices
            if len(stock) == 0:
                None
            else:
                stock['Name']=i
                tmp_stocks = tmp_stocks.append(stock,sort=False)
        except Exception:
            None

    tickers = tmp_stocks.Name.unique()

    for tik in tickers:
        tmp = tmp_stocks[tmp_stocks["Name"] == tik].sort_index()
        tmp['Close_change'] = tmp['Close'].pct_change()
        tmp["year"] = tmp.index.year
        tmp["Q"] = tmp.index.quarter
        tmp = tmp.merge(tmp.groupby(["year", "Q"])["Close"].sum().pct_change(), left_on = ["year", "Q"], right_index = True)

        DJI_stocks = DJI_stocks.append(tmp)

    DJI_stocks.to_csv("Data/DJI_stocks.csv")

def load_IXIC_stocks(start, end):
    # create empty dataframe
    global IXIC_stocks

    tmp_stocks = pd.DataFrame()

    # iterate over each symbol
    for (i, name, _) in IXIC:
        # print the symbol which is being downloaded
        #print( str(h) + str(' : ') + i, sep=',', end=',', flush=True)
        try:
            # download the stock price
            stock = []
            stock = yf.download(i,start=start, end=end, progress=False)

            # append the individual stock prices
            if len(stock) == 0:
                None
            else:
                stock['Name']=i
                tmp_stocks = tmp_stocks.append(stock,sort=False)
        except Exception:
            None

    tickers = tmp_stocks.Name.unique()

    for tik in tickers:
        tmp = tmp_stocks[tmp_stocks["Name"] == tik].sort_index()
        tmp['Close_change'] = tmp['Close'].pct_change()
        tmp["year"] = tmp.index.year
        tmp["Q"] = tmp.index.quarter
        tmp = tmp.merge(tmp.groupby(["year", "Q"])["Close"].sum().pct_change(), left_on = ["year", "Q"], right_index = True)

        IXIC_stocks = IXIC_stocks.append(tmp)

    IXIC_stocks.to_csv("Data/IXIC_stocks.csv")

def load_NYA_stocks(start, end):
    # create empty dataframe
    global NYA_stocks

    tmp_stocks = pd.DataFrame()

    # iterate over each symbol
    for (i, name, _) in NYA:
        # print the symbol which is being downloaded
        #print( str(h) + str(' : ') + i, sep=',', end=',', flush=True)
        try:
            # download the stock price
            stock = []
            stock = yf.download(i,start=start, end=end, progress=False)

            # append the individual stock prices
            if len(stock) == 0:
                None
            else:
                stock['Name']=i
                tmp_stocks = tmp_stocks.append(stock,sort=False)
        except Exception:
            None

    tickers = tmp_stocks.Name.unique()

    for tik in tickers:
        tmp = tmp_stocks[tmp_stocks["Name"] == tik].sort_index()
        tmp['Close_change'] = tmp['Close'].pct_change()
        tmp["year"] = tmp.index.year
        tmp["Q"] = tmp.index.quarter
        tmp = tmp.merge(tmp.groupby(["year", "Q"])["Close"].sum().pct_change(), left_on = ["year", "Q"], right_index = True)

        NYA_stocks = NYA_stocks.append(tmp)

    NYA_stocks.to_csv("Data/NYA_stocks.csv")

def load_Russell2000_stocks(start, end):
    # create empty dataframe
    global Russell2000_stocks

    tmp_stocks = pd.DataFrame()

    # iterate over each symbol
    for (i, name, _) in Russell2000:
        # print the symbol which is being downloaded
        #print( str(h) + str(' : ') + i, sep=',', end=',', flush=True)
        try:
            # download the stock price
            stock = []
            stock = yf.download(i,start=start, end=end, progress=False)

            # append the individual stock prices
            if len(stock) == 0:
                None
            else:
                stock['Name']=i
                tmp_stocks = tmp_stocks.append(stock,sort=False)
        except Exception:
            None

    tickers = tmp_stocks.Name.unique()

    for tik in tickers:
        tmp = tmp_stocks[tmp_stocks["Name"] == tik].sort_index()
        tmp['Close_change'] = tmp['Close'].pct_change()
        tmp["year"] = tmp.index.year
        tmp["Q"] = tmp.index.quarter
        tmp = tmp.merge(tmp.groupby(["year", "Q"])["Close"].sum().pct_change(), left_on = ["year", "Q"], right_index = True)

        Russell2000_stocks = Russell2000_stocks.append(tmp)

    Russell2000_stocks.to_csv("Data/Russell2000_stocks.csv")


#variables to store the read insider information for each market
SP500_insider = pd.DataFrame()
DJI_insider = pd.DataFrame()
IXIC_insider = pd.DataFrame()
NYA_insider = pd.DataFrame()
Russell2000_insider = pd.DataFrame()

#download the insider information for each market
def load_SP500_insider():
    global SP500_insider

    for (tik, _, _) in SP500:
        try:
            insider = finvizfinance(tik)
            df = insider.TickerInsideTrader()
            df["Ticker"] = tik
            df["Date"] = pd.to_datetime(df["Date"], format = "%b %d")
            df["Date"] = df["Date"] + pd.DateOffset(years = (datetime.date.today().year - df["Date"][0].year))
            df["Date"] = np.where(df["Date"].dt.month > datetime.date.today().month, df["Date"] + pd.DateOffset(years = -1), df["Date"])
            SP500_insider = SP500_insider.append(df)
        except:
            pass

    SP500_insider.to_csv("Data/SP500_insider.csv")

def load_DJI_insider():
    global DJI_insider

    for (tik, _, _) in DJI:
        try:
            insider = finvizfinance(tik)
            df = insider.TickerInsideTrader()
            df["Ticker"] = tik
            df["Date"] = pd.to_datetime(df["Date"], format = "%b %d")
            df["Date"] = df["Date"] + pd.DateOffset(years = (datetime.date.today().year - df["Date"][0].year))
            df["Date"] = np.where(df["Date"].dt.month > datetime.date.today().month, df["Date"] + pd.DateOffset(years = -1), df["Date"])
            DJI_insider = DJI_insider.append(df)
        except:
            pass

    DJI_insider.to_csv("Data/DJI_insider.csv")

def load_IXIC_insider():
    global IXIC_insider

    for (tik, _, _) in IXIC:
        try:
            insider = finvizfinance(tik)
            df = insider.TickerInsideTrader()
            df["Ticker"] = tik
            df["Date"] = pd.to_datetime(df["Date"], format = "%b %d")
            df["Date"] = df["Date"] + pd.DateOffset(years = (datetime.date.today().year - df["Date"][0].year))
            df["Date"] = np.where(df["Date"].dt.month > datetime.date.today().month, df["Date"] + pd.DateOffset(years = -1), df["Date"])
            IXIC_insider = IXIC_insider.append(df)
        except:
            pass

    IXIC_insider.to_csv("Data/IXIC_insider.csv")

def load_NYA_insider():
    global NYA_insider

    for (tik, _, _) in NYA:
        try:
            insider = finvizfinance(tik)
            df = insider.TickerInsideTrader()
            df["Ticker"] = tik
            df["Date"] = pd.to_datetime(df["Date"], format = "%b %d")
            df["Date"] = df["Date"] + pd.DateOffset(years = (datetime.date.today().year - df["Date"][0].year))
            df["Date"] = np.where(df["Date"].dt.month > datetime.date.today().month, df["Date"] + pd.DateOffset(years = -1), df["Date"])
            NYA_insider = NYA_insider.append(df)
        except:
            pass

    NYA_insider.to_csv("Data/NYA_insider.csv")

def load_Russell2000_insider():
    global Russell2000_insider

    for (tik, _, _) in Russell2000:
        try:
            insider = finvizfinance(tik)
            df = insider.TickerInsideTrader()
            df["Ticker"] = tik
            df["Date"] = pd.to_datetime(df["Date"], format = "%b %d")
            df["Date"] = df["Date"] + pd.DateOffset(years = (datetime.date.today().year - df["Date"][0].year))
            df["Date"] = np.where(df["Date"].dt.month > datetime.date.today().month, df["Date"] + pd.DateOffset(years = -1), df["Date"])
            Russell2000_insider = Russell2000_insider.append(df)
        except:
            pass

    Russell2000_insider.to_csv("Data/Russell2000_insider.csv")

#variables to store the combined lists of stocks, EPS and insider information for all the markets
stocks_final = pd.DataFrame()
full_tickersEPS = pd.DataFrame()
insider_final = pd.DataFrame()

#Entry Point
if __name__ == "__main__":
    #create QApplication object
    app = QApplication([])
    #add icon to window
    app.setWindowIcon(QIcon('stock_icon.ico'))

    #message box for the inicial prompt
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setWindowTitle("Update Data")
    msgBox.setText("Update Ticker and Stock Data Before Starting?")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.Yes)
    ret = msgBox.exec_()

    #if the the user wants to download the data
    if ret == QMessageBox.Yes:
        #start a progress dialog to track the data download progress
        progress = QProgressDialog("Downloading Stock Data...", "", 0, 15)
        progress.setWindowTitle("Downloading...")
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)

        progress.setValue(0)

        load_SP500()
        progress.setValue(1)

        load_DJI()
        progress.setValue(2)

        load_IXIC()
        progress.setValue(3)

        load_NYA()
        progress.setValue(4)

        load_Russell2000()
        progress.setValue(5)

        load_SP500_stocks(datetime.datetime(1986, 1, 1), datetime.date.today())
        progress.setValue(6)

        load_DJI_stocks(datetime.datetime(1986, 1, 1), datetime.date.today())
        progress.setValue(7)

        load_IXIC_stocks(datetime.datetime(1986, 1, 1), datetime.date.today())
        progress.setValue(8)

        load_NYA_stocks(datetime.datetime(1986, 1, 1), datetime.date.today())
        progress.setValue(9)

        load_Russell2000_stocks(datetime.datetime(1986, 1, 1), datetime.date.today())
        progress.setValue(10)

        load_SP500_insider()
        progress.setValue(11)

        load_DJI_insider()
        progress.setValue(12)

        load_IXIC_insider()
        progress.setValue(13)

        load_NYA_insider()
        progress.setValue(14)

        load_Russell2000_insider()
        progress.setValue(15)

    else:
        #if the the user wants to read the data
        SP500 = read_Pairs("SP500")
        DJI = read_Pairs("DJI")
        IXIC = read_Pairs("IXIC")
        NYA = read_Pairs("NYA")
        Russell2000 = read_Pairs("Russell2000")

        SP500_stocks = read_Stocks("SP500")
        DJI_stocks = read_Stocks("DJI")
        IXIC_stocks = read_Stocks("IXIC")
        NYA_stocks = read_Stocks("NYA")
        Russell2000_stocks = read_Stocks("Russell2000")

        SP500_stocks['Date'] = pd.to_datetime(SP500_stocks['Date'])
        DJI_stocks['Date'] = pd.to_datetime(DJI_stocks['Date'])
        IXIC_stocks['Date'] = pd.to_datetime(IXIC_stocks['Date'])
        NYA_stocks['Date'] = pd.to_datetime(NYA_stocks['Date'])
        Russell2000_stocks['Date'] = pd.to_datetime(Russell2000_stocks['Date'])

        SP500_stocks.set_index('Date', inplace=True)
        DJI_stocks.set_index('Date', inplace=True)
        IXIC_stocks.set_index('Date', inplace=True)
        NYA_stocks.set_index('Date', inplace=True)
        Russell2000_stocks.set_index('Date', inplace=True)

        SP500_insider = read_Insider("SP500")
        DJI_insider = read_Insider("DJI")
        IXIC_insider = read_Insider("IXIC")
        NYA_insider = read_Insider("NYA")
        Russell2000_insider = read_Insider("Russell2000")

    #append the read data to the combined data lists
    full_tickersEPS = full_tickersEPS.append(pd.DataFrame(np.array(SP500)[:, ::-2], columns=["EPS", "Name"])).append(pd.DataFrame(np.array(DJI)[:, ::-2], columns=["EPS", "Name"])).append(pd.DataFrame(np.array(IXIC)[:, ::-2], columns=["EPS", "Name"])).append(pd.DataFrame(np.array(NYA)[:, ::-2], columns=["EPS", "Name"])).append(pd.DataFrame(np.array(Russell2000)[:, ::-2], columns=["EPS", "Name"]))
    full_tickersEPS = full_tickersEPS.drop_duplicates(subset=['Name'])

    stocks_final = stocks_final.append(SP500_stocks, sort=False).append(DJI_stocks, sort=False).append(IXIC_stocks, sort=False).append(NYA_stocks, sort=False).append(Russell2000_stocks, sort=False)

    insider_final = insider_final.append(SP500_insider, sort=False).append(DJI_insider, sort=False).append(IXIC_insider, sort=False).append(NYA_insider, sort=False).append(Russell2000_insider, sort=False)

    #after all the data has been downloaded/parsed, start the main window
    widget = StockScreener()
    #show the main window
    widget.ui.show()
    #in the end exit the program when the close button is clicked
    sys.exit(app.exec_())
