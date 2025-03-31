import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import Row

from brewery.silver import BrewerySilver, schema


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.master("local[1]").appName("Test Brewery Silver").getOrCreate()


@pytest.fixture
def brewery_silver(mock_config):
    return BrewerySilver(mock_config)


def test_apply_transformations(spark, brewery_silver):
    input_data = [
        Row(
            id="1",
            name=" Brewery A ",
            brewery_type="micro",
            address_1="123 Main St",
            address_2=None,
            address_3=None,
            city="CityA",
            state_province="StateA",
            postal_code="12345",
            country="CountryA",
            longitude="10.123",
            latitude="20.456",
            phone="123-456-7890",
            website_url="http://brewerya.com",
            state="StateA",
            street="123 Main St",
        ),
        Row(
            id="2",
            name="Brewery B",
            brewery_type="nano",
            address_1="456 Side St",
            address_2=None,
            address_3=None,
            city="CityB",
            state_province="StateB",
            postal_code="67890",
            country="CountryB",
            longitude="invalid",
            latitude="30.789",
            phone="987-654-3210",
            website_url="http://breweryb.com",
            state="StateB",
            street="456 Side St",
        ),
        Row(
            id="1",
            name=" Brewery A ",
            brewery_type="micro",
            address_1="123 Main St",
            address_2=None,
            address_3=None,
            city="CityA",
            state_province="StateA",
            postal_code="12345",
            country="CountryA",
            longitude="10.123",
            latitude="20.456",
            phone="123-456-7890",
            website_url="http://brewerya.com",
            state="StateA",
            street="123 Main St",
        ),
    ]
    input_df = spark.createDataFrame(input_data, schema)

    transformed_df = brewery_silver._apply_transformations(input_df)

    result = transformed_df.collect()

    row_1 = next(filter(lambda r: r.id == "1", result))
    row_2 = next(filter(lambda r: r.id == "2", result))

    assert len(result) == 2  # Duplicates should be removed
    assert row_1.name == "Brewery A"  # Whitespace should be trimmed
    assert row_1.longitude == 10.123  # Longitude should be cast to double
    assert row_2.longitude is None  # Invalid longitude should be handled
    assert row_1.latitude == 20.456  # Latitude should be cast to double
    assert row_2.latitude == 30.789  # Latitude should be cast to double
    assert row_1.brewery_type == "micro"  # Brewery type should be preserved


def test_run(mocker, spark, brewery_silver):
    # type: ignore
    mocker.patch(
        "pyspark.sql.SparkSession.read",
        return_value=spark.createDataFrame([], schema=schema),
    )
    mocker.patch("pyspark.sql.DataFrame.write", autospec=True)

    brewery_silver.run()

    # Verify that the read and write methods were called
    SparkSession.read.format.assert_called_once_with("json") # type: ignore
    SparkSession.read.format().schema.assert_called_once() # type: ignore
    SparkSession.read.format().schema().load.assert_called_once() # type: ignore
