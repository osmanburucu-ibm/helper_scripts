# Other automation readme

## entitled registry

### login into entitled registry

```sh
export ENTITLED_REGISTRY=cp.icr.io
export ENTITLED_REGISTRY_USER=cp
export ENTITLED_REGISTRY_KEY=XXXXXYYYYYZZZZZAAAAAAABBBBBB
docker login "$ENTITLED_REGISTRY" -u "$ENTITLED_REGISTRY_USER" -p "$ENTITLED_REGISTRY_KEY
```

### pull images from registry

```sh
docker pull cp.icr.io/cp/<myimage-area>/<myimage:version>
```
