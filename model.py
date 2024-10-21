from pydantic import BaseModel, HttpUrl, conlist, constr, validator
from typing import List, Optional, Dict, Any

class Date(BaseModel):
    expression: str
    begin: str
    end: Optional[str] = None
    date_type: Optional[str] = None

class Extent(BaseModel):
    number: str
    unit: str

class Agent(BaseModel):
    name: str
    agent_type: str

class Container(BaseModel):
    top_container: Optional[str] = None
    top_container_indicator: Optional[str] = None
    sub_container: Optional[str] = None
    sub_container_indicator: Optional[str] = None
    sub_sub_container: Optional[str] = None
    sub_sub_container_indicator: Optional[str] = None

class DigitalObject(BaseModel):
    href: HttpUrl
    label: str
    identifier: Optional[str] = None
    is_representative: str
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Optional[List[Dict[str, Any]]] = None
    thumbnail_href: Optional[HttpUrl] = None
    rights_statement: Optional[str] = None

class Component(BaseModel):
    id: str
    collection_id: str
    title: str
    title_filing_si: Optional[str] = None
    repository: str
    level: str
    collection_name: str
    dates: Optional[List[Date]] = None
    extents: Optional[List[Extent]] = None
    languages: Optional[List[str]] = None
    creators: Optional[List[Agent]] = None
    names: Optional[List[Agent]] = None
    subjects: Optional[List[str]] = None
    places: Optional[List[str]] = None
    abstract: Optional[List[str]] = None
    accessrestrict: Optional[List[str]] = None
    scopecontent: Optional[List[str]] = None
    acqinfo: Optional[List[str]] = None
    accruals: Optional[List[str]] = None
    altformavail: Optional[List[str]] = None
    appraisal: Optional[List[str]] = None
    arrangement: Optional[List[str]] = None
    bibliography: Optional[List[str]] = None
    bioghist: Optional[List[str]] = None
    custodhist: Optional[List[str]] = None
    fileplan: Optional[List[str]] = None
    note: Optional[List[str]] = None
    odd: Optional[List[str]] = None
    originalsloc: Optional[List[str]] = None
    otherfindaid: Optional[List[str]] = None
    phystech: Optional[List[str]] = None
    prefercite: Optional[List[str]] = None
    processinfo: Optional[List[str]] = None
    relatedmaterial: Optional[List[str]] = None
    separatedmaterial: Optional[List[str]] = None
    userestrict: Optional[List[str]] = None
    materialspec: Optional[List[str]] = None
    physloc: Optional[List[str]] = None

    containers: Optional[List[Container]] = None
    digital_objects: Optional[List[DigitalObject]] = None
    components: Optional[List['Component']] = None  # Using a forward reference for recursive type

# Example usage:
# component = Component(id='1', collection_id='col1', title='Title', repository='Repo', level='item', collection_name='Collection Name')
