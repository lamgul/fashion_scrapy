from dependency_injector import providers, containers

from src.libs.resource.eyesmag.eyesmag_repository import EyesMagRepository
from src.libs.resource.fashionchingu.fashionchingu_repository import FashionChinguRepository
from src.libs.resource.fashioninsight.fashioninsight_repository import FashionInsightRepository
from src.libs.resource.harpersbazaar.harpersbazaar_repository import HarpersBazaarRepository
from src.libs.resource.kmodes.kmodes_repository import KmodesRepository
from src.libs.resource.krazefashion.krazefashion_repository import KrazeFashionRepository
from src.libs.resource.krazemedia.krazemedia_repository import KrazeMediaRepository
from src.libs.resource.oncuration.oncuration_repository import OncurationRepository
from src.libs.resource.seoulinspired.seoulinspired_repository import SeoulInspiredRepository
from src.libs.resource.unnielooks.unnielooks_repository import UnnieLooksRepository
from src.libs.resource.voguekorea.voguekorea_repository import VogueKoreaRepository
from src.libs.resource.yesstyle.yesstyle_repository import YesstyleRepository


class RepositoryContainer(containers.DeclarativeContainer):
    session = providers.Dependency()

    voguekorea_repository = providers.Resource(VogueKoreaRepository, session=session)
    fashionchingu_repository = providers.Resource(FashionChinguRepository, session=session)
    eyesmag_repository = providers.Resource(EyesMagRepository, session=session)
    fashioninsight_repository = providers.Resource(FashionInsightRepository, session=session)
    unnielooks_repository = providers.Resource(UnnieLooksRepository, session=session)
    yesstyle_repository = providers.Resource(YesstyleRepository, session=session)
    harpersbazaar_repository = providers.Resource(HarpersBazaarRepository, session=session)
    kmodes_repository = providers.Resource(KmodesRepository, session=session)
    krazefashion_repository = providers.Resource(KrazeFashionRepository, session=session)
    krazemedia_repository = providers.Resource(KrazeMediaRepository, session=session)
    oncuration_repository = providers.Resource(OncurationRepository, session=session)
    seoulinspired_repository = providers.Resource(SeoulInspiredRepository, session=session)
