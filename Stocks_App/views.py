from django.shortcuts import render
from django.db import connection
from datetime import datetime


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def index(request):
    return render(request, 'index.html')


def Query_Results(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT DI.Name, Round(sum(totalInvestment),3) as totalSum
FROM  DiverseInvestment DI
GROUP BY DI.ID, DI.Name
ORDER BY totalSum DESC
            """)
        sql_res1 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT BI.Symbol, Investor.Name, BI.maxShares
FROM  BiggestInvestor BI INNER JOIN  Investor ON BI.ID = Investor.ID
ORDER BY  BI.Symbol, Investor.Name;
                """)
        sql_res2 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT OneBuyingChange.Date, OneBuyingChange.Symbol, Investor.Name
FROM (
SELECT OOBE.tDate AS Date, FC.Symbol, ((FC.priceAfterBuy - OOBE.oldPrice)/OOBE.oldPrice *100) AS percentChange,OOBE.id
FROM OnlyOneBuyingExtended OOBE INNER JOIN FirstChange FC on OOBE.Symbol = FC.Symbol) AS OneBuyingChange
INNER JOIN Investor On OneBuyingChange.id = Investor.ID
WHERE OneBuyingChange.percentChange > 3;
                    """)
        sql_res3 = dictfetchall(cursor)
    return render(request, 'Query_Results.html', {'sql_res1': sql_res1,
                                                  'sql_res2': sql_res2,
                                                  'sql_res3': sql_res3})


def Add_Transactions(request):
    is_id_valid = True
    if request.method == 'POST' and request.POST:
        ID = int(request.POST["ID"])
        tSum = int(request.POST["tSum"])
        with connection.cursor() as cursor:
            cursor.execute("""SELECT *
                          FROM Investor I
                          WHERE I.ID = %s;""", [ID])
            sql_res2 = dictfetchall(cursor)
            if not sql_res2:
                is_id_valid = False
            else:
                today = datetime.today().strftime('%Y-%m-%d')
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT T.TQuantity
                              FROM Transactions T
                              WHERE T.ID = %s AND T.tDate=%s;""", [ID, today])
                    sql_res3 = dictfetchall(cursor)
                    if sql_res3:
                        old_quantity = sql_res3.pop(0).get("TQuantity")
                        with connection.cursor() as cursor:
                            cursor.execute("""UPDATE Investor SET AvailableCash =AvailableCash - %s
                                           WHERE Investor.ID = %s""", [old_quantity, ID])
                        with connection.cursor() as cursor:
                            cursor.execute("""DELETE FROM Transactions  WHERE Transactions.tDate = %s AND Transactions.ID = %s
                                           """, [today, ID])

                    with connection.cursor() as cursor:
                        cursor.execute("""INSERT INTO Transactions (tDate, ID, TQuantity) 
                                        VALUES (%s,%s,%s)""", [today, ID, tSum])
                    with connection.cursor() as cursor:
                        cursor.execute("""UPDATE Investor SET AvailableCash =AvailableCash+ %s
                                        WHERE Investor.ID = %s""", [tSum, ID])

    with connection.cursor() as cursor:
        cursor.execute(""" SELECT TOP 10 *
                           FROM Transactions T
                           ORDER BY  T.tDate DESC, T.ID DESC ;
        """)
        sql_res1 = dictfetchall(cursor)
    return render(request, 'Add_Transaction.html', {'sql_res1': sql_res1,
                                                    'is_id_valid': is_id_valid})


def Buy_Stocks(request):
    today = datetime.today().strftime('%Y-%m-%d')
    is_id_valid = True
    is_symbol_valid = True
    is_cash_enough = True
    is_prev_buying = False
    if request.method == 'POST' and request.POST:
        ID = int(request.POST["ID"])
        Symbol = str(request.POST["Symbol"])
        BQuantity = int(request.POST["BQuantity"])
        with connection.cursor() as cursor:
            cursor.execute("""SELECT I.ID
                                      FROM Investor I
                                      WHERE I.ID = %s;""", [ID])
            sql_res2 = dictfetchall(cursor)
        with connection.cursor() as cursor:
            cursor.execute("""SELECT C.Symbol
                                      FROM Company C
                                      WHERE C.Symbol = %s;""", [Symbol])
            sql_res3 = dictfetchall(cursor)

        if (not sql_res2) or (not sql_res3):
            if not sql_res2:
                is_id_valid = False
            if not sql_res3:
                is_symbol_valid = False
        if is_id_valid and is_symbol_valid:  # if both id and symbol are valid
            with connection.cursor() as cursor:
                cursor.execute("""SELECT *
                                  FROM Buying B
                                  WHERE B.Symbol = %s AND B.tDate = %s""", [Symbol, today])
                sql_res4 = dictfetchall(cursor)
            if not sql_res4:  # if there wasn't buying of this investor and this company today
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT *
                                      FROM Stock S
                                      WHERE S.Symbol = %s AND S.tDate = %s""", [Symbol, today])
                    sql_res5 = dictfetchall(cursor)

                with connection.cursor() as cursor:
                    cursor.execute("""SELECT *
                                          FROM Stock S
                                          WHERE S.Symbol =%s
                                          ORDER BY S.tDate DESC""", [Symbol])
                    sql_res6 = dictfetchall(cursor)
                    share_price = sql_res6.pop(0).get("Price")

                    if not sql_res5:  # if we need to add share value to Stocks
                        with connection.cursor() as cursor:
                            cursor.execute("""INSERT INTO Stock (Symbol, tDate, Price) 
                                                VALUES (%s,%s,%s)""", [Symbol, today, share_price])

                    with connection.cursor() as cursor:  # check if available cash is valid
                        cursor.execute("""SELECT Investor.AvailableCash
                                          FROM Investor
                                          WHERE  Investor.ID =%s;""", [ID])
                        sql_res7 = dictfetchall(cursor)
                        a_cash = sql_res7.pop(0).get("AvailableCash")

                    if a_cash >= BQuantity * share_price:
                        with connection.cursor() as cursor:
                            cursor.execute("""INSERT INTO Buying (tDate, ID, Symbol,BQuantity) 
                                              VALUES (%s,%s,%s,%s)""", [today, ID, Symbol, BQuantity])
                        with connection.cursor() as cursor:
                            cursor.execute("""UPDATE Investor SET AvailableCash =AvailableCash - (%s * %s)
                                           WHERE Investor.ID = %s""", [BQuantity, share_price, ID])
                    else:
                        is_cash_enough = False
            else:
                is_prev_buying=True

    with connection.cursor() as cursor:
        cursor.execute(""" SELECT TOP 10 B.tDate, B.ID,B.Symbol, ROUND(B.BQuantity*S.Price,2) AS Payed
                           FROM Buying B INNER JOIN Stock S on B.Symbol = S.Symbol and B.tDate = S.tDate
                           ORDER BY Payed DESC, B.ID DESC;

        """)
        sql_res1 = dictfetchall(cursor)
    return render(request, 'Buy_Stocks.html', {'sql_res1': sql_res1,
                                               'is_id_valid':is_id_valid,
                                               'is_symbol_valid':is_symbol_valid,
                                               'is_cash_enough':is_cash_enough,
                                               'is_prev_buying':is_prev_buying})
