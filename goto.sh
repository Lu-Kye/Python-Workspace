#!/usr/bin/env bash
case $1 in
    ro)
        p=/Users/lujian/Documents/unity-workspace/RO
        cd $p
        ;;
    blog)
        p=/Users/lujian/Documents/doc-workspace/Lu-Kye.github.io
        cd $p
        ;;
    xxd)
        p=/Users/lujian/Documents/go-workspace/xxd-server
        cd $p
        export GOPATH=$p/server		
        ;;
    xxd1)
        p=/Users/lujian/Documents/go-workspace/xxd-server1
        cd $p
        export GOPATH=$p/server		
        ;;
    xxd-js)
        p=/Users/lujian/Documents/ch-workspace/xxd-js-2
        cd $p
        ;;
    test)
        p=/Users/lujian/Documents/go-workspace/go-test
        export GOPATH=$p
        cd $p
        ;;
    plane)
        p=/Users/lujian/Documents/projects/HitPlane
        export GOPATH=$p
        cd $p
        ;;
    planeserver)
        p=/Users/lujian/Documents/projects/HitPlaneServer
        export GOPATH=$p
        cd $p
        ;;
esac
