import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import Row

from brewery.gold import BreweryGold


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.master("local[1]").appName("Test Brewery Gold").getOrCreate()


@pytest.fixture
def brewery_gold(mock_config):
    return BreweryGold(mock_config)


def test_aggregate_data(spark, brewery_gold):
    input_data = [
        Row(type="micro", country="CountryA"),
        Row(type="nano", country="CountryB"),
        Row(type="micro", country="CountryA"),
    ]
    input_df = spark.createDataFrame(input_data)

    aggregated_data = brewery_gold._aggregate_data(input_df)

    per_type_result = aggregated_data["per_type"].collect()
    per_country_result = aggregated_data["per_country"].collect()

    assert len(per_type_result) == 2  # Two types: micro, nano
    assert len(per_country_result) == 2  # Two countries: CountryA, CountryB

    assert any(row["type"] == "micro" and row["count"] == 2 for row in per_type_result)
    assert any(row["country"] == "CountryA" and row["count"] == 2 for row in per_country_result)


def test_run(mocker, spark, brewery_gold):
    mocker.patch(
        "pyspark.sql.SparkSession.read",
        return_value=spark.createDataFrame([], schema="type STRING, country STRING"),
    )
    mocker.patch("pyspark.sql.DataFrame.write", autospec=True)

    brewery_gold.run()

    # Verify that the read and write methods were called
    SparkSession.read.parquet.assert_called_once()  # type: ignore
    SparkSession.read.parquet().write.mode.assert_called()  # type: ignore
