import os, subprocess, sys, argparse
import collections

BuildInfo = collections.namedtuple('BuildInfo', 'nginx brotli commit_range branch tag pull_request event_type is_travis')

def main():
    parser = argparse.ArgumentParser(description='Build some docker images.')
    parser.add_argument('--nginx-version', dest='nginx_version', default=os.environ.get('NGINX_VERSION'), help='The nginx to build')
    parser.add_argument('--brotli-version', dest='brotli_version', default=os.environ.get('BROTLI_VERSION'), help='The brotli to build')
    parser.add_argument('--commit-range', dest='commit_range', default=os.environ.get('TRAVIS_COMMIT_RANGE', 'HEAD...HEAD'), help='the commit range')
    parser.add_argument('--branch', dest='branch', default=os.environ.get('TRAVIS_BRANCH', ""), help='the commit branch')
    parser.add_argument('--tag', dest='tag', default=os.environ.get('TRAVIS_TAG', False), help='the commit tag')
    parser.add_argument('--pull-request', dest='pull_request', default=os.environ.get('TRAVIS_PULL_REQUEST', "false"), help='it is a PR?')
    parser.add_argument('--event-type', dest='event_type', default=os.environ.get('TRAVIS_EVENT_TYPE', ""), help='The event type which trigger the build')
    parser.add_argument('--travis', dest='travis', default=os.environ.get('TRAVIS', "false"), help='is travis')

    args = parser.parse_args()

    buildInfo = BuildInfo(
        nginx=args.nginx_version,
        brotli=args.brotli_version,
        commit_range=args.commit_range,
        branch=args.branch if len(args.branch) > 0 else False,
        tag=args.tag,
        pull_request=True if args.pull_request != "false" else False,
        event_type=args.event_type,
        is_travis=True if args.travis == "true" else False,
    )

    print args, buildInfo

    run_build(buildInfo)

def run_command_exit(command, exit_message):
    if run_command(command) != 0:
        print exit_message
        sys.exit(1)


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print output.strip()

    rc = process.poll()

    return rc


def run_build(buildInfo):
    if not buildInfo.nginx or not buildInfo.brotli:
        print "please provide a NGINX_VERSION and a BROTLI_VERSION"
        sys.exit(1)

    is_tag = False
    is_pr = False
    is_release = False
    is_master = False
    start_build = False
    push_image = False

    print "TRAVIS_BRANCH=%s" % buildInfo.branch
    print "TRAVIS_TAG=%s" % buildInfo.tag
    print "TRAVIS_PULL_REQUEST=%s" % buildInfo.pull_request
    print "NGINX_VERSION=%s" % buildInfo.nginx
    print "BROTLI_VERSION=%s" % buildInfo.brotli
    print "TRAVIS_COMMIT_RANGE=%s" % buildInfo.commit_range

    if buildInfo.pull_request:
        print " > This is a PR"
        is_pr = True

    if buildInfo.tag:
        print " > This is a Tag"
        is_tag = True
        image = "ekino/nginx-brotli:%s-%s" % (buildInfo.nginx, buildInfo.brotli)
        start_build = True  # on tag build all images
        push_image = True
    elif buildInfo.branch == 'master' and not is_pr:
        print " > This is a master commit"
        is_master = True
        image = "ekino/nginx-brotli:latest-%s-%s" % (buildInfo.nginx, buildInfo.brotli)
    else:
        image = "ekino/nginx-brotli:other-%s-%s" % (buildInfo.nginx, buildInfo.brotli)

    if buildInfo.event_type == "cron":
        print " > This is a cron event"
        image = "ekino/nginx-brotli:nightly-%s-%s" % (buildInfo.nginx, buildInfo.brotli)
        start_build = True
        push_image = True

    if is_pr and is_tag:
        print "cannot be a tag and a pr"
        sys.exit(1)

    if (is_pr or is_master):
        start_build = True
        push_image = is_master

    print "is_pr: %s" % is_pr
    print "is_tag: %s" % is_tag
    print "is_master: %s" % is_master
    print "is_release: %s" % is_release
    print "image: %s" % image
    print "start_build: %s" % start_build
    print "push_image: %s" % push_image

    if start_build:
        build_args = "--build-arg NGINX_VERSION=%s --build-arg NGX_BROTLI_COMMIT=%s" % (buildInfo.nginx, buildInfo.brotli)

        cmd = "docker build -t %s %s --no-cache ." % (image, build_args)

        print "> Run: %s" % cmd

        run_command_exit(cmd, "fail to build the image")

        print ""
        print "You can now test the image with the following command:\n   $ docker run --rm -ti %s" % image

    if push_image:
        run_command_exit("docker login --username %s --password %s" % (os.environ.get('DOCKER_USERNAME'), os.environ.get('DOCKER_PASSWORD')), "unable to login to docker")
        run_command_exit("docker push %s" % image, "unable to login to docker")


if __name__ == "__main__":
    main()