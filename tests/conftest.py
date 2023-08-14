import ape
from ape_tokens import tokens
from ape.types import AddressType
import pytest

YEAR = int(365.25 * 24 * 60 * 60)


@pytest.fixture(scope="session")
def duration():
    yield 3 * YEAR


@pytest.fixture(scope="session")
def ychad(accounts):
    return accounts[ape.convert("ychad.eth", AddressType)]


@pytest.fixture(scope="session")
def ytrades(accounts):
    return accounts[ape.convert("ytrades.ychad.eth", AddressType)]


@pytest.fixture(scope="session")
def recipient(accounts):
    yield accounts["0x0000000000000000000000000000000000031337"]


@pytest.fixture(scope="session")
def cold_storage(accounts):
    yield accounts["0x000000000000000000000000000000000000C001"]


@pytest.fixture(scope="module")
def token():
    return tokens["YFI"]


@pytest.fixture(scope="module")
def another_token():
    return tokens["DAI"]


@pytest.fixture(scope="module")
def start_time(chain):
    yield chain.pending_timestamp + YEAR


@pytest.fixture(scope="module")
def end_time(start_time, duration):
    yield int(start_time + duration)


@pytest.fixture(scope="module")
def cliff_duration(duration):
    yield duration // 6


@pytest.fixture(scope="module")
def vesting_target(project, ychad):
    yield ychad.deploy(project.VestingEscrowSimple)


@pytest.fixture(scope="module")
def vyper_donation(accounts):
    # 0x70CCBE10F980d80b7eBaab7D2E3A73e87D67B775
    yield accounts[ape.convert("vyperlang.eth", AddressType)]


@pytest.fixture(scope="module")
def vesting_factory(project, ychad, vesting_target, vyper_donation):
    yield ychad.deploy(project.VestingEscrowFactory, vesting_target, vyper_donation)


@pytest.fixture(scope="module")
def amount(token):
    yield ape.convert(f"100 {token.symbol()}", int)


@pytest.fixture(scope="module")
def another_amount(another_token):
    yield ape.convert(f"10 {another_token.symbol()}", int)


@pytest.fixture(scope="module")
def open_claim():
    yield True


@pytest.fixture(scope="module")
def support_vyper():
    yield 10


@pytest.fixture(scope="module")
def support_amount(amount, support_vyper):
    yield amount * support_vyper // 10_000


@pytest.fixture(scope="module")
def vesting(
    project,
    ychad,
    recipient,
    vesting_factory,
    token,
    amount,
    support_amount,
    start_time,
    cliff_duration,
    open_claim,
    duration,
    support_vyper,
):
    token.approve(vesting_factory, amount + support_amount, sender=ychad)
    receipt = vesting_factory.deploy_vesting_contract(
        token,
        recipient,
        amount,
        duration,
        start_time,
        cliff_duration,
        open_claim,
        support_vyper,
        sender=ychad,
    )
    escrow = vesting_factory.VestingEscrowCreated.from_receipt(receipt)[0]
    yield project.VestingEscrowSimple.at(escrow.escrow)
