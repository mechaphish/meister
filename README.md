# Meister

This repo is for the "master" component of the CGC.

## Run

    mv .env.development .env
    meister

## CGC TI Client

```
import meister.cgc.ticlient

api = meister.cgc.ticlient.TiClient(HOST, PORT, USER, PASS)

# data retrieval (see TiRetrieval)
api.getStatus()

# data submission (see TiSubmission)
api.uploadRCB("LUNGE_00005",
              ('LUNGE_00005_1', open("path", 'rb').read()),
              ('LUNGE_00005_2', open("path", 'rb').read()))

api.uploadPOV("LUNGE_00005", "team", N_THROWS, POV_DATA)
```

## Testing

    nosetests tests
