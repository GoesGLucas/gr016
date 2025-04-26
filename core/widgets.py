from django_select2.forms import ModelSelect2Widget
from .models import ItemInspecao  # Ou Produto, dependendo do modelo

class ItemAutocompleteWidget(ModelSelect2Widget):
    model = ItemInspecao
    search_fields = ['codigo_produto__icontains']
    dependent_fields = {}
    url = 'autocomplete/item/'  # Esse nome deve bater com a URL que você vai criar
