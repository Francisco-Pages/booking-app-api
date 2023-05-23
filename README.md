# booking-app-api

database design

# rental unit
    
    title 
    description
    custom link
    languages
    status
    images (foreignfield, table)
    property type
    max_guests

    amenities (each is a boolean field, description field next to some values) and amentities description table
        
        popular 

        essentials
        airconditioning
        cleaning products
        cooking basics
        dedicated workspace
        dishes and silverware
        washer
        dryer
        hair dryer
        heating
        hot tub
        kitchen
        pool
        tv
        wifi

        bathroom

        bathtub
        bidet
        body soap
        conditioner
        hot water outdoor shower
        shampoo
        shower gel

        bedroom and laundry

        essentials
        bed linens
        clothing storage
        extra pillows and blankets
        hangers
        iron
        drying rack
        mosquito net
        room darkening shades
        safe

        entertainment

        arcade games
        books and reading material
        bowling alley
        climbing wall
        ethernet connection
        exercise equipment
        games console
        life size games
        piano 
        ping pong table
        record player
        sound system

        family

        baby bath
        baby monitor
        childrens bikes
        childrens playroom
        baby safe gates
        changing table
        childrens books and toys
        childrens dinnerware
        crib
        fireplace guards
        high chair
        outdoor playground
        packnplay/travel crib
        table corner guards
        window guards

        heating and cooling

        ceiling fan 
        heating
        indoor fireplace
        portable fans

        kitchen and dining

        baking sheet
        bbq utensils
        breadmaker
        blender
        coffee
        coffee maker
        dining table
        dishwasher
        freezer
        hot water kettle
        kitchenette
        microwave
        mini fridge
        oven
        refrigerator
        rice maker
        stove
        toaster
        trash compactor
        wine glasses

        location features

        beach access
        lake acccess
        laundromat nearby
        private entrance
        resort access
        ski access
        waterfront

        outdoor

        backyard
        bbq grill
        beach essentials
        bikes
        boat slip
        fire pit
        hammock
        kayak
        outdoor dining area
        outdoor furniture
        outdoor kitchen
        patio or balcony
        sun loungers

        parking and facilities

        elevator
        ev charger
        free parking on premises
        hockey rink
        free street parking
        gym
        hot tub 
        paid parking off premises
        paid parking on premises
        sauna
        pool
        single level home

        services

        breakfast
        cleaning available during stay
        long term stays allowed
        luggage dropoff allowed

    location
        neighborhood description
        getting around
        location sharing
        address (table)
            ...
            coordinates
            ...
    rooms and spaces(foreignkey, table: room type, room name, bed, couch, tv, bathroom type, shower type)
        room type
        room name
        bed type
        couch type
        tv (yes or no)
        bathroom type (half or full)
        shower type (tub, regadera, jaccuzzi, outdoor)

    accessibility - add accessibility descriptions table
        entrance
        entrance description
        parking
        parking description
        adaptive equipment
        adaptive equipment description
        door width
        door width description
        stairs 

    guest safety
        carbon monoxide alarm
        fire extinguisher
        first aid kit
        smoke alarm
        unsuitable for children 2-12
        unsuitable for infants under 2
        pool/hot tub without a gate or lock
        nearby body of water
        climbing or play structure
        heights without rails or protection
        potentially dangerous animals
        security cameras/audio recording devices
        must climb stairs
        potential for noise
        pet(s) live on property
        no parking on property
        some spaces are shared
        weapons on property

    pricing
        night price
        smart pricing
        min price
        max price
        listing currency
        weekly discount
        monthly discount
        additional charges (foreignkey) add table for prices
            ...
            pet fee
            extra guest
            transport
            ...
        taxes
        taxes description

    calendar availability
        min stay
        max stay
        advance notice
        prep time
        availability window (how many days in advance)
        restricted check in days
        restricted check out days
        blocked dates (foreignkey table, rental unit id, datetime start, datetime end)

    policies and rules
        cancellation policy
        instant book
        house rules
            pets allowed
            events allowed
            smoking, vaping, e-cigarettes allowed
            commercial photography and filming allowed
            quiet hours
            max guests
            additional rules 
                rule text
        guest requirements
        laws and regulations
        primary use of listing

    info for guests
        pre-booking details 
            check in window
            checkout time
            guidebook 
                name
                type
                description
                address
                image
            interaction preferences
            check-in method
        post-booking preferences
            house manual
                question (ex: wifi name)
                answer (ex: wifi password)
            checkin method instructions
            wifi details

reservations
    guest
    rental unit reserved
    check in day
    checkout day
    num of guests
    travel insurance
    payment method
    nightly subtotal
    additional charges selected (foreignfield: additional charges)
    taxes
    total
    status

