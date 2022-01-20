from django.db import models


class Buying(models.Model):
    tdate = models.OneToOneField('Stock', models.DO_NOTHING, db_column='tDate', primary_key=True)
    id = models.ForeignKey('Investor', models.DO_NOTHING, db_column='ID')
    symbol = models.ForeignKey('Stock', models.DO_NOTHING, db_column='Symbol', related_name='+')
    bquantity = models.IntegerField(db_column='BQuantity', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buying'
        unique_together = (('tdate', 'id', 'symbol'),)


class Company(models.Model):
    symbol = models.CharField(db_column='Symbol', primary_key=True, max_length=10)  # Field name made lowercase.
    sector = models.CharField(db_column='Sector', max_length=40, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=40, blank=True,
                                null=True)  # Field name made lowercase.
    founded = models.IntegerField(db_column='Founded', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Company'


class Investor(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=40, blank=True, null=True)  # Field name made lowercase.
    availablecash = models.IntegerField(db_column='AvailableCash', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Investor'


class Stock(models.Model):
    symbol = models.OneToOneField(Company, models.DO_NOTHING, db_column='Symbol',
                                  primary_key=True)  # Field name made lowercase.
    tdate = models.DateField(db_column='tDate')  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Stock'
        unique_together = (('symbol', 'tdate'),)


class Transactions(models.Model):
    tdate = models.DateField(db_column='tDate', primary_key=True)  # Field name made lowercase.
    id = models.ForeignKey(Investor, models.DO_NOTHING, db_column='ID')  # Field name made lowercase.
    tquantity = models.IntegerField(db_column='TQuantity', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Transactions'
        unique_together = (('tdate', 'id'),)
