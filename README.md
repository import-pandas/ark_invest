# ark_invest
daily weekday report of @arkinvest ETF activity + data collection

# This script was created to:
1. Extract and save daily csv's from ARKInvest's holdings.
2. Quick command-line report about security additions and removals within each of the 6 ARK ETFs ($ARKK, $ARKW, $ARKG, $ARKQ, $ARKF, $PRNT)
3. Quick command-line report about significant changes in security positions within each of the 6 ARK ETFs ($ARKK, $ARKW, $ARKG, $ARKQ, $ARKF, $PRNT)
4. Option to save day-over-day changes in holdings within each of the 6 ARK ETFs ($ARKK, $ARKW, $ARKG, $ARKQ, $ARKF, $PRNT)

# Current suggested process flow as follows:
From command-line:
1. Run 'import_status()':
      - Saves current csv from ARKInvest site for each of the 6 ETFs as 'temp.csv'
      - Identifies whether the temp file is new, or a duplicate of your previous day's run. *ARK appears to upload new csv's at 7PM EST.
      - If step 2 does not identify a new import, the program will exit().
2. Run 'allocation()': 
      - Compares ticker presence within the two most recent confirmed files. 
3. Run 'changes(significance)':
      - Identifies significant increases or decreases in shares within the two most recent confirmed files. Significance parameter = float.
      - Example: changes(6.0) -> Within each ETF, return shares increase >= 6.0% AND return shares decrease <= -6.0%
4. Run 'all_dfs()' if you would like to access each of the ETF's most recent day-over-day report. The function will return a list of pandas dataframes. *See below:
      - DoD_reports = all_dfs()
      - arkk = DoD_reports[0]
      - arkw = DoD_reports[1]
      - arkg = DoD_reports[2]
      - arkq = DoD_reports[3]
      - arkf = DoD_reports[4]
      - prnt = DoD_reports[5]

# Still a work in progress but wanted to share with everyone asap. Curious to see if this is helpful!
Some items I am working through now:
1. What if ARK updates some of the files, but not all?
2. Is it convenient to exit program after identifying that a new csv is not available?
3. You will notice a 'queue' variable that I am playing around with. This is to potentially only pass eligible import items to different functions. 
4. Considering using a SQLite db file instead of saving files to subdirectories (obviously not ideal)
5. Considering dashboard or API endpoint on simplimoku.com (a simple site for ichimoku charting and ichimoku signal screener)
