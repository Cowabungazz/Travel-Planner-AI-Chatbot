from typing import List

from pydantic import BaseModel


class Flight(BaseModel):
    departure: str
    arrival: str
    date: str
    time: str
    duration: str
    stopovers: List[str]


class Accommodation(BaseModel):
    name: str
    location: str
    image: str
    price: str
    availability: bool
    description: str
    discount: str


class Destination(BaseModel):
    country: str
    state: str
    city: str


class Currency(BaseModel):
    code: str
    symbol: str


class Activity(BaseModel):
    uuid: str
    title: str
    description: str
    highlights: str
    additionalInfo: float
    priceExcludes: str
    latitude: float
    longitude: float
    address: str
    minPax: int
    maxPax: int
    basePrice: float
    currency: Currency
    typeName: str
    photoUrl: str
    businessHoursFrom: str
    businessHoursTo: str
    averageDelivery: str
    hotelPickup: bool
    airportPickup: bool


class Basket(BaseModel):
    destinations: List[Destination]
    flights: List[Flight]
    accommodation: List[Accommodation]
    itinerary: List[Activity]