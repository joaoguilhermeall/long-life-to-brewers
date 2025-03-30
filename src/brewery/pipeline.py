from brewery.bronze import BreweryBronze
from brewery.common import BreweryConfig


class BreweryPipeline:
    """Brewery pipeline class to manage the data pipeline."""

    def __init__(self) -> None:
        self._config = BreweryConfig()

    async def bronze(self) -> None:
        """Bronze stage of the pipeline."""
        bronze_instance = BreweryBronze(self._config)
        await bronze_instance.run()

    def silver(self) -> None:
        """Silver stage of the pipeline."""
        pass

    def gold(self) -> None:
        """Gold stage of the pipeline."""

    async def run(self) -> None:
        """Run the pipeline."""
        await self.bronze()
        self.silver()
        self.gold()
