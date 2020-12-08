from observations.models import Datasourcetype


def test_create_datasource_type():
    datasourcetype = Datasourcetype.objects.create(name="Datasourcetype 1")
    assert datasourcetype.name == "Datasourcetype 1"
