from typing import Any, List, TypeVar, Callable, Type, cast, Optional

from backend.constants import FOODY_FILES_CDN_BASE, FOODY_COUNTRY, FOODY_ALLERGEN_DATA

LOCALE = None
T = TypeVar("T")


def set_locale(locale):
    global LOCALE
    LOCALE = locale


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except Exception as err:
            _ = err  # Just to avoid warnings
    assert False, f"Unable to parse data"


def from_float(x: Any) -> float:
    assert isinstance(x, float) and not isinstance(x, bool)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_boolean(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Translation:
    locale: Optional[str]
    value: Optional[str]

    def __init__(self, locale, value):
        self.locale = locale
        self.value = value

    @staticmethod
    def from_dict(value) -> 'Translation':
        return Translation(LOCALE, value)

    def to_dict(self):
        return {
            'locale': from_union([from_str, from_none], self.locale),
            'value': from_union([from_str, from_none], self.value),
        }

    def __add__(self, other):
        return self


class ObjectWithTranslations:
    translations: Optional[List[Translation]]

    def __init__(self, translations):
        self.translations = translations

    @staticmethod
    def from_dict(value: str) -> 'ObjectWithTranslations':
        if value:
            translations = from_union([lambda x: from_list(Translation.from_dict, x), from_none], [value])
        else:
            translations = list()
        return ObjectWithTranslations(translations)

    def to_dict(self):
        translations = from_union([lambda x: from_list(lambda y: to_class(Translation, y), x), from_none],
                                  self.translations)
        return {
            'translations': translations
        }

    def __add__(self, other):
        self.translations += other.translations
        return self


class Option:
    name: Optional[ObjectWithTranslations]
    short_description: Optional[ObjectWithTranslations]
    price: Optional[float]

    def __init__(self, name, short_description, price):
        self.name = name
        self.short_description = short_description
        self.price = price

    @staticmethod
    def from_dict(obj: Any) -> 'Option':
        name = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('displayName'))
        short_description = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('description'))
        price = from_union([from_float, from_int, from_none], obj.get('priceAdd'))
        return Option(name, short_description, price)

    def to_dict(self) -> dict:
        name = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none], self.name)
        short_description = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none],
                                       self.short_description)
        price = from_union([from_float, from_int, from_none], self.price)
        return {
            'name': name,
            'shortDescription': short_description,
            'price': price,
        }

    def __add__(self, other):
        self.name += other.name
        self.short_description += other.short_description
        return self


class OptionGroup:
    identifier: Optional[int]
    name: Optional[ObjectWithTranslations]
    short_description: Optional[ObjectWithTranslations]
    min_cardinality: Optional[int]
    max_cardinality: Optional[int]
    allow_multiple_selections: Optional[bool]
    options: List[Option]

    def __init__(self, identifier, name, short_description, min_cardinality,
                 max_cardinality, allow_multiple_selections, options):
        self.identifier = identifier
        self.name = name
        self.short_description = short_description
        self.min_cardinality = min_cardinality
        self.max_cardinality = max_cardinality
        self.allow_multiple_selections = allow_multiple_selections
        self.options = options

    @staticmethod
    def from_dict(obj: Any) -> 'OptionGroup':
        identifier = from_union([from_str, from_none], obj.get('id'))
        name = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('displayName'))
        short_description = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('description'))
        min_cardinality = from_union([from_int, from_none], obj.get('minNumOfMod'))
        max_cardinality = from_union([from_int, from_none], obj.get('maxNumOfMod'))
        options = from_union([lambda x: from_list(Option.from_dict, x), from_none], obj.get('modifiers'))
        options = options or list()
        allow_multiple_selections = max_cardinality > len(options)
        return OptionGroup(identifier, name, short_description, min_cardinality, max_cardinality,
                           allow_multiple_selections, options)

    def to_dict(self) -> dict:
        identifier = from_union([from_str, from_none], self.identifier)
        name = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none], self.name)
        short_description = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none],
                                       self.short_description)
        min_cardinality = from_union([from_int, from_none], self.min_cardinality)
        max_cardinality = from_union([from_int, from_none], self.max_cardinality)
        allow_multiple_selections = from_union([from_boolean, from_none], self.allow_multiple_selections)
        options = from_union([lambda x: from_list(lambda y: to_class(Option, y), x), from_none], self.options)
        return {
            'identifier': identifier,
            'name': name,
            'shortDescription': short_description,
            'minCardinality': min_cardinality,
            'maxCardinality': max_cardinality,
            'allowMultipleSelections': allow_multiple_selections,
            'options': options,
        }

    def __add__(self, other):
        self.name += other.name
        self.short_description += other.short_description
        other_options = other.options or list()
        for i, item in enumerate(other_options):
            self.options[i] += item
        return self


class Variant:
    name: Optional[ObjectWithTranslations]
    price: Optional[float]
    discount: Optional[float]

    def __init__(self, name, price, discount):
        self.name = name
        self.price = price
        self.discount = discount

    @staticmethod
    def from_dict(obj: Any) -> 'Variant':
        name = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('displayName'))
        price = from_union([from_float, from_int, from_none], obj.get('price'))
        discount = from_union([from_float, from_int, from_none], obj.get('discount'))
        return Variant(name, price, discount)

    def to_dict(self) -> dict:
        name = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none], self.name)
        price = from_union([from_float, from_int, from_none], self.price)
        discount = from_union([from_float, from_int, from_none], self.discount)
        return {
            'name': name,
            'price': price,
            'discount': discount,
        }

    def __add__(self, other):
        self.name += other.name
        return self


class Offer:
    identifier: str
    name: Optional[ObjectWithTranslations]
    short_description: Optional[ObjectWithTranslations]
    long_description: Optional[ObjectWithTranslations]
    price: Optional[float]
    discount: Optional[float]
    vat: Optional[float]
    image_url: Optional[str]
    allergens: Optional[List[str]]
    option_group_identifiers: Optional[List[int]]
    variants: Optional[List[Variant]]
    option_groups: Optional[List[OptionGroup]]

    def __init__(self, identifier, name, short_description, long_description, price, discount,
                 vat, image_url, allergens, option_group_identifiers, variants, option_groups):
        self.identifier = identifier
        self.name = name
        self.short_description = short_description
        self.long_description = long_description
        self.price = price
        self.discount = discount
        self.vat = vat
        self.image_url = image_url
        self.allergens = allergens
        self.option_group_identifiers = option_group_identifiers
        self.variants = variants
        self.option_groups = option_groups

    @staticmethod
    def from_dict(obj: Any) -> 'Offer':
        identifier = from_union([from_str, from_none], obj.get('id'))
        name = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('displayName'))
        short_description = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('description'))
        long_description = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('longDescr'))
        price = from_union([from_float, from_int, from_none], obj.get('price'))
        discount = from_union([from_float, from_int, from_none], obj.get('discount'))
        vat = from_union([from_float, from_int, from_none], obj.get('vat'))
        image_name = from_union([from_str, from_none], (obj.get('popupImages') and obj['popupImages'][0]) or None)
        image_url = image_name and (FOODY_FILES_CDN_BASE + image_name)
        allergens = from_union([lambda x: from_list(from_str, x), lambda x: from_list(from_int, x), from_none],
                               obj.get('allergens'))
        allergens = allergens or list()
        allergen_values = list()
        for allergen in allergens:
            allergen_values.append(FOODY_ALLERGEN_DATA.get(allergen) or allergen)
        option_group_identifiers = from_union([lambda x: from_list(from_int, x), from_none],
                                              obj.get('option_group_identifiers')) or list()
        variants = from_union([lambda x: from_list(Variant.from_dict, x), from_none], obj.get('sizedItemsPerParent'))
        variants = variants or list()
        option_groups = from_union([lambda x: from_list(OptionGroup.from_dict, x), from_none],
                                   obj.get('modifierCategories')) or list()

        return Offer(identifier, name, short_description, long_description, price, discount, vat, image_url,
                     allergen_values, option_group_identifiers, variants, option_groups)

    def to_dict(self) -> dict:
        name = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none], self.name)
        short_description = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none],
                                       self.short_description)
        long_description = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none], self.long_description)
        price = from_union([from_float, from_int, from_none], self.price)
        discount = from_union([from_float, from_int, from_none], self.discount)
        vat = from_union([from_float, from_int, from_none], self.vat)
        image_url = from_union([from_str, from_none], self.image_url)
        allergens = from_union([lambda x: from_list(from_str, x), lambda x: from_list(from_int, x), from_none],
                               self.allergens)
        option_group_identifiers = from_union([lambda x: from_list(from_str, x), from_none],
                                              self.option_group_identifiers)
        variants = from_union([lambda x: from_list(lambda y: to_class(Variant, y), x), from_none], self.variants)

        return {
            'name': name,
            'shortDescription': short_description,
            'longDescription': long_description,
            'price': price,
            'discount': discount,
            'vat': vat,
            'imageURL': image_url,
            'allergens': allergens,
            'optionGroupIdentifiers': option_group_identifiers,
            'variants': variants,
        }

    def to_variant(self):
        return Variant(self.name, self.price, self.discount)

    def __add__(self, other):
        self.name += other.name
        self.short_description += other.short_description
        self.long_description += other.long_description
        other_variants = other.variants or list()
        for i, item in enumerate(other_variants):
            self.variants[i] += item
        return self


class SizedItem:
    name: Optional[ObjectWithTranslations]
    description: Optional[ObjectWithTranslations]
    size_item_ids: Optional[List[str]]

    def __init__(self, name, description, size_item_ids):
        self.name = name
        self.description = description
        self.size_item_ids = size_item_ids

    @staticmethod
    def from_dict(obj) -> 'SizedItem':
        name = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('displayName'))
        description = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('description'))
        size_item_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get('sizeItemIds')) or list()
        return SizedItem(name, description, size_item_ids)


class Category:
    name: Optional[ObjectWithTranslations]
    offers: Optional[List[Offer]]
    sized_items: Optional[List[SizedItem]]

    def __init__(self, name, offers, sized_items):
        self.name = name
        self.offers = offers
        self.sized_items = sized_items

    @staticmethod
    def from_dict(obj: Any) -> 'Category':
        name = from_union([ObjectWithTranslations.from_dict, from_none], obj.get('description'))
        offers = from_union([lambda x: from_list(Offer.from_dict, x), from_none], obj.get('items')) or list()
        sized_items = from_union([lambda x: from_list(SizedItem.from_dict, x), from_none],
                                 obj.get('sizedItemsPerParent')) or list()
        return Category(name, offers, sized_items)

    def to_dict(self) -> dict:
        name = from_union([lambda y: to_class(ObjectWithTranslations, y), from_none], self.name)
        offers = from_union([lambda x: from_list(lambda y: to_class(Offer, y), x), from_none], self.offers)
        return {
            'name': name,
            'offers': offers
        }

    def prepare_variants(self):
        offer_dict = {offer.identifier: offer for offer in self.offers}
        self.offers = list()
        for sized_item in self.sized_items:
            offer_ids = list(sized_item.size_item_ids)
            offer = offer_dict.pop(offer_ids.pop(0))
            for variant_id in offer_ids:
                offer.variants.append(offer_dict.pop(variant_id).to_variant())
            self.offers.append(offer)
        self.offers += offer_dict.values()

    def __add__(self, other):
        self.name += other.name
        other_offers = other.offers or list()
        for i, item in enumerate(other_offers):
            self.offers[i] += item
        return self


class StoreAddress:
    line1: Optional[str]
    line2: Optional[str]
    region: Optional[str]
    city: Optional[str]
    postcode: Optional[str]
    country: Optional[str]

    def __init__(self, line1, line2, region, city, postcode, country):
        self.line1 = line1
        self.line2 = line2
        self.region = region
        self.city = city
        self.postcode = postcode
        self.country = country

    @staticmethod
    def from_dict(obj: Any) -> 'StoreAddress':
        line1 = from_union([from_none, from_str], obj.get('line1'))
        line2 = from_union([from_none, from_str], obj.get('line2')) or str()
        region = from_union([from_none, from_str], obj.get('region')) or str()
        city = from_union([from_none, from_str], obj.get('city')) or str()
        postcode = from_union([from_none, from_str], obj.get('postcode')) or str()
        country = FOODY_COUNTRY
        return StoreAddress(line1, line2, region, city, postcode, country)

    def to_dict(self) -> dict:
        line1 = from_union([from_str, from_none], self.line1)
        line2 = from_union([from_str, from_none], self.line2)
        region = from_union([from_str, from_none], self.region)
        city = from_union([from_str, from_none], self.city)
        postcode = from_union([from_str, from_none], self.postcode)
        country = from_union([from_str, from_none], self.country)
        return {
            'line1': line1,
            'line2': line2,
            'region': region,
            'city': city,
            'postcode': postcode,
            'country': country,
        }

    def __add__(self, other):
        return self


class StoreInfo:
    name: Optional[str]
    alias: Optional[str]
    address: Optional[StoreAddress]
    logo_url: Optional[str]
    background_url: Optional[str]

    def __init__(self, name, alias, address, logo_url, background_url):
        self.name = name
        self.alias = alias
        self.address = address
        self.logo_url = logo_url
        self.background_url = background_url

    @staticmethod
    def from_dict(obj: Any) -> 'StoreInfo':
        name = from_union([from_str, from_none], obj.get('name'))
        alias = from_union([from_str, from_none], obj.get('slug'))
        address = from_union([StoreAddress.from_dict, from_none], {'line1': obj.get('address')})
        logo_image = from_union([from_str, from_none], obj.get('logo'))
        logo_url = logo_image and (FOODY_FILES_CDN_BASE + logo_image)
        background_image = from_union([from_str, from_none], obj.get('headerImage'))
        background_url = background_image and (FOODY_FILES_CDN_BASE + background_image)
        return StoreInfo(name, alias, address, logo_url, background_url)

    def to_dict(self) -> dict:
        name = from_union([from_str, from_none], self.name)
        alias = from_union([from_str, from_none], self.alias)
        logo_url = from_union([from_str, from_none], self.logo_url)
        background_url = from_union([from_str, from_none], self.background_url)
        return {
            'name': name,
            'alias': alias,
            'address': self.address.to_dict(),
            'logoURL': logo_url,
            'backgroundURL': background_url,
        }

    def __add__(self, other):
        return self


class Result:
    store_info: Optional[StoreInfo]
    categories: Optional[List[Category]]
    option_groups: Optional[List[OptionGroup]]

    def __init__(self, store_info, categories, option_groups):
        self.store_info = store_info
        self.categories = categories
        self.option_groups = option_groups

    def prepare_option_groups(self):
        option_groups = list()
        option_group_ids = set()
        if not self.categories:
            return
        for category in self.categories:
            for offer in category.offers:
                offer.option_group_identifiers = offer.option_group_identifiers or list()
                for option_group in offer.option_groups:
                    offer.option_group_identifiers.append(option_group.identifier)
                    if option_group.identifier in option_group_ids:
                        continue
                    option_group_ids.add(option_group.identifier)
                    option_groups.append(option_group)
        self.option_groups = option_groups

    def prepare_variants_for_each_category(self):
        for category in self.categories:
            category.prepare_variants()

    @staticmethod
    def from_dict(obj: Any):
        store_info = from_union([StoreInfo.from_dict, from_none], obj.get('store_info'))
        categories = from_union([lambda x: from_list(Category.from_dict, x), from_none],
                                obj.get('categories')) or list()
        option_groups = from_union([lambda x: from_list(OptionGroup.from_dict, x), from_none],
                                   obj.get('option_groups')) or list()
        return Result(store_info, categories, option_groups)

    def to_dict(self):
        store_info = from_union([lambda y: to_class(StoreInfo, y), from_none], self.store_info)
        categories = from_union([lambda x: from_list(lambda y: to_class(Category, y), x), from_none], self.categories)
        option_groups = from_union([lambda x: from_list(lambda y: to_class(OptionGroup, y), x), from_none],
                                   self.option_groups)
        return {
            'storeInfo': store_info,
            'categories': categories,
            'optionGroups': option_groups
        }

    def __add__(self, other):
        if self.store_info and other.store_info:
            self.store_info += other.store_info

        other_categories = other.categories or list()
        for i, item in enumerate(other_categories):
            self.categories[i] += item

        other_option_groups = other.option_groups or list()
        for i, item in enumerate(other_option_groups):
            self.option_groups[i] += item
        return self
