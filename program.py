"""This sample script demonstrates how to invoke the Data View REST API"""

import configparser
import copy
import datetime
import random
import traceback
from ocs_sample_library_preview import (DataView, Field, FieldSource, OCSClient, Query,
                                        SdsStream, SdsType, SdsTypeCode, 
                                        SdsTypeProperty, SummaryDirection, SdsSummaryType)

# Sample Data Information
SAMPLE_TYPE_ID_1 = 'Time_SampleType1'
SAMPLE_TYPE_ID_2 = 'Time_SampleType2'
SAMPLE_STREAM_ID_1 = 'dvTank2'
SAMPLE_STREAM_NAME_1 = 'Tank2'
SAMPLE_STREAM_ID_2 = 'dvTank100'
SAMPLE_STREAM_NAME_2 = 'Tank100'
SAMPLE_FIELD_TO_CONSOLIDATE_TO = 'temperature'
SAMPLE_FIELD_TO_CONSOLIDATE = 'ambient_temp'
SAMPLE_FIELD_TO_ADD_UOM_COLUMN_1 = 'pressure'
SAMPLE_FIELD_TO_ADD_UOM_COLUMN_2 = 'temperature'
SUMMARY_FIELD_ID = 'pressure'
SUMMARY_TYPE_1 = 'Mean'
SUMMARY_TYPE_2 = 'Total'

# Data View Information
SAMPLE_DATAVIEW_ID = 'DataView_Sample'
SAMPLE_DATAVIEW_NAME = 'DataView_Sample_Name'
SAMPLE_DATAVIEW_DESCRIPTION = 'A Sample Description that describes that this '\
    'Data View is just used for our sample.'
SAMPLE_QUERY_ID = 'stream'
SAMPLE_QUERY_STRING = 'dvTank*'
SAMPLE_INTERVAL = '00:20:00'


def suppress_error(sds_call):
    """Suppresses an error thrown by SDS"""
    try:
        sds_call()
    except Exception as error:
        print(('Encountered Error: {error}'.format(error=error)))


def find_field(fieldset_fields, field_source):
    """Find a field by field source"""
    for field in fieldset_fields:
        if field.Source == field_source:
            return field
    return None


def find_fieldset(fieldsets, fieldset_query_id):
    """Find a fieldset by query id"""
    for fieldset in fieldsets:
        if fieldset.QueryId == fieldset_query_id:
            return fieldset
    return None


def find_field_key(fieldset_fields, field_source, key):
    """Find a field by source and key"""
    for field in fieldset_fields:
        if field.Source == field_source and any(key in s for s in field.Keys):
            return field
    return None


def main(test=False):
    """This function is the main body of the Data View sample script"""
    exception = None

    config = configparser.ConfigParser()
    config.read('config.ini')

    print('--------------------------------------------------------------------')
    print(' ######                      #    #                 ######  #     # ')
    print(' #     #   ##   #####   ##   #    # # ###### #    # #     #  #   #  ')
    print(' #     #  #  #    #    #  #  #    # # #      #    # #     #   # #   ')
    print(' #     # #    #   #   #    # #    # # #####  #    # ######     #    ')
    print(' #     # ######   #   ###### #    # # #      # ## # #          #    ')
    print(' #     # #    #   #   #    #  #  #  # #      ##  ## #          #    ')
    print(' ######  #    #   #   #    #   ##   # ###### #    # #          #    ')
    print('--------------------------------------------------------------------')

    # Step 1
    print()
    print('Step 1: Authenticate against OCS')
    ocs_client = OCSClient(config.get('Access', 'ApiVersion'),
                           config.get('Access', 'Tenant'),
                           config.get('Access', 'Resource'),
                           config.get('Credentials', 'ClientId'),
                           config.get('Credentials', 'ClientSecret'))

    namespace_id = config.get('Configurations', 'Namespace')

    print(namespace_id)
    print(ocs_client.uri)

    try:

        # Step 2
        print()
        print('Step 2: Create types, streams, and data')
        times = create_data(namespace_id, ocs_client)
        sample_start_time = times[0]
        sample_end_time = times[1]

        # Step 3
        print()
        print('Step 3: Create a data view')
        dataview = DataView(SAMPLE_DATAVIEW_ID,
                            SAMPLE_DATAVIEW_NAME, SAMPLE_DATAVIEW_DESCRIPTION)
        ocs_client.DataViews.postDataView(namespace_id, dataview)

        # Step 4
        print()
        print('Step 4: Retrieve the data view')
        dataview = ocs_client.DataViews.getDataView(
            namespace_id, SAMPLE_DATAVIEW_ID)
        print(dataview.toJson())

        # Step 5
        print()
        print('Step 5: Add a query for data items')
        query = Query(SAMPLE_QUERY_ID, value=SAMPLE_QUERY_STRING)
        dataview.Queries = [query]
        # No Data View returned, success is 204
        ocs_client.DataViews.putDataView(namespace_id, dataview)

        # Step 6
        print()
        print('Step 6: View items found by the query')
        print('List data items found by the query:')
        data_items = ocs_client.DataViews.getResolvedDataItems(
            namespace_id, SAMPLE_DATAVIEW_ID, SAMPLE_QUERY_ID)
        print(data_items.toJson())

        print('List ineligible data items found by the query:')
        data_items = ocs_client.DataViews.getResolvedIneligibleDataItems(
            namespace_id, SAMPLE_DATAVIEW_ID, SAMPLE_QUERY_ID)
        print(data_items.toJson())

        # Step 7
        print()
        print('Step 7: View fields available to include in the data view')
        available_fields = ocs_client.DataViews.getResolvedAvailableFieldSets(
            namespace_id, SAMPLE_DATAVIEW_ID)
        print(available_fields.toJson())

        # Step 8
        print()
        print('Step 8: Include some of the available fields')
        dataview.DataFieldSets = available_fields.Items
        ocs_client.DataViews.putDataView(namespace_id, dataview)

        print('List available field sets:')
        available_fields = ocs_client.DataViews.getResolvedAvailableFieldSets(
            namespace_id, SAMPLE_DATAVIEW_ID)
        print(available_fields.toJson())

        print('Retrieving data from the data view:')
        dataview_data = ocs_client.DataViews.getDataInterpolated(
            namespace_id, SAMPLE_DATAVIEW_ID, start_index=sample_start_time,
            end_index=sample_end_time, interval=SAMPLE_INTERVAL)
        print(str(dataview_data))
        print(len(dataview_data))
        assert len(dataview_data) > 0, 'Error getting data view data'

        # Step 9
        print()
        print('Step 9: Group the data view')
        grouping = Field(source=FieldSource.Id,
                         label='{DistinguisherValue} {FirstKey}')
        dataview.GroupingFields = [grouping]
        # No DataView returned, success is 204
        ocs_client.DataViews.putDataView(namespace_id, dataview)

        print('Retrieving data from the data view:')
        dataview_data = ocs_client.DataViews.getDataInterpolated(
            namespace_id, SAMPLE_DATAVIEW_ID, start_index=sample_start_time,
            end_index=sample_end_time, interval=SAMPLE_INTERVAL)
        print(str(dataview_data))
        assert len(dataview_data) > 0, 'Error getting data view data'

        # Step 10
        print()
        print('Step 10: Identify data items')
        identify = dataview.GroupingFields.pop()
        dataview_dataitem_fieldset = find_fieldset(
            dataview.DataFieldSets, SAMPLE_QUERY_ID)
        dataview_dataitem_fieldset.IdentifyingField = identify
        # No Data View returned, success is 204
        ocs_client.DataViews.putDataView(namespace_id, dataview)

        print('Retrieving data from the data view:')
        dataview_data = ocs_client.DataViews.getDataInterpolated(
            namespace_id, SAMPLE_DATAVIEW_ID, start_index=sample_start_time,
            end_index=sample_end_time, interval=SAMPLE_INTERVAL)
        print(str(dataview_data))
        assert len(dataview_data) > 0, 'Error getting data view data'

        # Step 11
        print()
        print('Step 11: Consolidate data fields')
        field1 = find_field_key(dataview_dataitem_fieldset.DataFields,
                                FieldSource.PropertyId, SAMPLE_FIELD_TO_CONSOLIDATE_TO)
        field2 = find_field_key(dataview_dataitem_fieldset.DataFields,
                                FieldSource.PropertyId, SAMPLE_FIELD_TO_CONSOLIDATE)
        print(field1.toJson())
        print(field2.toJson())
        field1.Keys.append(SAMPLE_FIELD_TO_CONSOLIDATE)
        dataview_dataitem_fieldset.DataFields.remove(field2)
        # No Data View returned, success is 204
        ocs_client.DataViews.putDataView(namespace_id, dataview)

        print('Retrieving data from the data view:')
        dataview_data = ocs_client.DataViews.getDataInterpolated(
            namespace_id, SAMPLE_DATAVIEW_ID, start_index=sample_start_time,
            end_index=sample_end_time, interval=SAMPLE_INTERVAL)
        print(str(dataview_data))
        assert len(dataview_data) > 0, 'Error getting data view data'

        # Step 12
        print()
        print('Step 12: Add Units of Measure Column')
        field1 = find_field_key(dataview_dataitem_fieldset.DataFields,
                                FieldSource.PropertyId, SAMPLE_FIELD_TO_ADD_UOM_COLUMN_1)
        field2 = find_field_key(dataview_dataitem_fieldset.DataFields,
                                FieldSource.PropertyId, SAMPLE_FIELD_TO_ADD_UOM_COLUMN_2)
        
        field1.IncludeUom = True
        field2.IncludeUom = True
        ocs_client.DataViews.putDataView(namespace_id, dataview)

        print('Retrieving data from the data view:')
        dataview_data = ocs_client.DataViews.getDataInterpolated(
            namespace_id, SAMPLE_DATAVIEW_ID, start_index=sample_start_time,
            end_index=sample_end_time, interval=SAMPLE_INTERVAL)
        print(str(dataview_data))
        assert len(dataview_data) > 0, 'Error getting data view data'

        # Step 13
        print()
        print('Step 13: Add Summaries Columns')
        # find the field for which we want to add a couple summary columns
        ref_field = find_field_key(dataview_dataitem_fieldset.DataFields,
                                FieldSource.PropertyId, SAMPLE_FIELD_TO_ADD_UOM_COLUMN_1)
        
        # deep copy the field twice so we can change properties
        field1 = copy.deepcopy(ref_field)
        field2 = copy.deepcopy(ref_field)
        
        # set the summary properties and add the fields to the data fields array
        field1.SummaryDirection = SummaryDirection.Forward
        field1.SummaryType = SdsSummaryType[SUMMARY_TYPE_1]
        field2.SummaryDirection = SummaryDirection.Forward
        field2.SummaryType = SdsSummaryType[SUMMARY_TYPE_2]

        dataview_dataitem_fieldset.DataFields.append(field1)
        dataview_dataitem_fieldset.DataFields.append(field2)
        
        ocs_client.DataViews.putDataView(namespace_id, dataview)

        print('Retrieving data from the data view:')
        dataview_data = ocs_client.DataViews.getDataInterpolated(
            namespace_id, SAMPLE_DATAVIEW_ID, start_index=sample_start_time,
            end_index=sample_end_time, interval=SAMPLE_INTERVAL)
        print(str(dataview_data))
        assert len(dataview_data) > 0, 'Error getting data view data'

    except Exception as error:
        print((f'Encountered Error: {error}'))
        print()
        traceback.print_exc()
        print()
        exception = error

    finally:

        #######################################################################
        # Data View deletion
        #######################################################################

        # Step 14
        print()
        print('Step 14: Delete sample objects from OCS')
        print('Deleting data view...')

        suppress_error(lambda: ocs_client.DataViews.deleteDataView(
            namespace_id, SAMPLE_DATAVIEW_ID))

        # check, including assert is added to make sure we deleted it
        dataview = None
        try:
            dataview = ocs_client.DataViews.getDataView(
                namespace_id, SAMPLE_DATAVIEW_ID)
        except Exception as error:
            # Exception is expected here since Data View has been deleted
            dataview = None
        finally:
            assert dataview is None, 'Delete failed'
            print('Verification OK: Data View deleted')

        print('Deleting sample streams...')
        suppress_error(lambda: ocs_client.Streams.deleteStream(
            namespace_id, SAMPLE_STREAM_ID_1))
        suppress_error(lambda: ocs_client.Streams.deleteStream(
            namespace_id, SAMPLE_STREAM_ID_2))

        print('Deleting sample types...')
        suppress_error(lambda: ocs_client.Types.deleteType(
            namespace_id, SAMPLE_TYPE_ID_1))
        suppress_error(lambda: ocs_client.Types.deleteType(
            namespace_id, SAMPLE_TYPE_ID_2))

        if test and exception is not None:
            raise exception
    print('Complete!')


def create_data(namespace_id, ocs_client: OCSClient):
    """Creates sample data for the script to use"""

    double_type = SdsType('doubleType', SdsTypeCode.Double)
    datetime_type = SdsType('dateTimeType', SdsTypeCode.DateTime)

    pressure_property = SdsTypeProperty('pressure', False, double_type, uom='bar')
    temperature_property = SdsTypeProperty(SAMPLE_FIELD_TO_CONSOLIDATE_TO, False,
                                            double_type, uom='degree Celsius')
    ambient_temperature_property = SdsTypeProperty(SAMPLE_FIELD_TO_CONSOLIDATE, False,
                                            double_type, uom='degree Celsius')
    time_property = SdsTypeProperty('time', True, datetime_type)

    sds_type_1 = SdsType(
        SAMPLE_TYPE_ID_1, SdsTypeCode.Object, [
            pressure_property, temperature_property, time_property],
        description='This is a sample Sds type for storing Pressure type '
                    'events for Data Views')

    sds_type_2 = SdsType(
        SAMPLE_TYPE_ID_2, SdsTypeCode.Object, [
            pressure_property, ambient_temperature_property, time_property],
        description='This is a new sample Sds type for storing Pressure type '
                    'events for Data Views')

    print('Creating SDS Types...')
    ocs_client.Types.getOrCreateType(namespace_id, sds_type_1)
    ocs_client.Types.getOrCreateType(namespace_id, sds_type_2)

    stream1 = SdsStream(
        SAMPLE_STREAM_ID_1,
        SAMPLE_TYPE_ID_1,
        SAMPLE_STREAM_NAME_1,
        'A Stream to store the sample Pressure events')

    stream2 = SdsStream(
        SAMPLE_STREAM_ID_2,
        SAMPLE_TYPE_ID_2,
        SAMPLE_STREAM_NAME_2,
        'A Stream to store the sample Pressure events')

    print('Creating SDS Streams...')
    ocs_client.Streams.createOrUpdateStream(namespace_id, stream1)
    ocs_client.Streams.createOrUpdateStream(namespace_id, stream2)

    sample_start_time = datetime.datetime.now() - datetime.timedelta(hours=1)
    sample_end_time = datetime.datetime.now()

    values1 = []
    values2 = []

    def value_with_time(timestamp, value, field_name, value2):
        """Formats a JSON data object"""
        return f'{{"time": "{timestamp}", "pressure": {str(value)}, "{field_name}": {str(value2)}}}'

    print('Generating values...')
    for i in range(1, 30, 1):
        timestamp = (sample_start_time + datetime.timedelta(minutes=i * 2)
                     ).isoformat(timespec='seconds')
        val1 = value_with_time(timestamp, random.uniform(
            0, 100), SAMPLE_FIELD_TO_CONSOLIDATE_TO, random.uniform(50, 70))
        val2 = value_with_time(timestamp, random.uniform(
            0, 100), SAMPLE_FIELD_TO_CONSOLIDATE, random.uniform(50, 70))

        values1.append(val1)
        values2.append(val2)

    print('Sending values...')
    ocs_client.Streams.insertValues(
        namespace_id,
        SAMPLE_STREAM_ID_1,
        str(values1).replace("'", ""))
    ocs_client.Streams.insertValues(
        namespace_id,
        SAMPLE_STREAM_ID_2,
        str(values2).replace("'", ""))

    return (sample_start_time, sample_end_time)


if __name__ == '__main__':
    main()
