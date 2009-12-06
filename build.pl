#!/usr/bin/perl -w
# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski
#
# Skrypt budujący dystrybucję:
# - koryguje numer wersji
# - nakłada tag
# - odpala budujący setup
# - wgrywa na mekka

use strict;
use FindBin;
use File::Spec::Functions;
use File::Copy;
use Tie::File;
use File::Path;

my $MODULE_NAME = "mekk.xmind";
my $PYTHON_VERSION = "py2.5";

chdir $FindBin::Bin or die "chdir failed: $!\n";

#################################################################
# Funkcje pomocnicze
#################################################################

sub ask_yes_no {
    my $question = shift;
    my $x;
    do {
        {
          local $/ = undef;
          print "$question (y/n): ";
        }
        $x = <STDIN>;
        $x =~ s/[\s\r\n]+//g;
        $x = lc($x);
    } while $x !~ /^[yn]$/;
    if ($x eq 'y') {
        return 1;
    } else {
        return 0;
    }
}

#################################################################
# Ustalenie numerka wersji, skorygowanie go w setup.py
# nałożenie tagu.
#################################################################

my $what = shift @ARGV || '';
unless ($what =~ /^(major|minor|patch|devel|rebuild)$/) {
    print "Usage:\n$0 [major|minor|patch|devel|rebuild]\n";
    exit(1);
}

my $version;

if ($what ne 'devel') {
    my $status = `hg status src README.txt setup.py setup.cfg`;
    if ($status) {
        die "Uncommited changes found\n";
    }
    my @newest = (0,0,0);
    open(F, "hg tags|");
    while(<F>) {
        if(/^(\d+)\.(\d+)\.(\d+)\b/) {
            if( $1 > $newest[0]
                  || ($1 == $newest[0]
                        && ($2 > $newest[1]
                              || ($2 == $newest[1] && $3 > $newest[2])))) {
                @newest = ($1, $2, $3);
            }
        }
    }
    close(F);

    if ($what eq 'major') {
        $version = join('.', $newest[0]+1, 0, 0);
    }
    elsif ($what eq 'minor') {
        $version = join('.', $newest[0], $newest[1]+1, 0);
    }
    elsif ($what eq 'patch') {
        $version = join('.', $newest[0], $newest[1], $newest[2]+1);
    }
    elsif ($what eq 'rebuild') {
        $version = join('.', $newest[0], $newest[1], $newest[2]);
    }
    else {
        die "Ups\n";
    }

    print "Creating version: $version"
      . ($what eq 'rebuild' ? " (rebuild - don't do it if already published)": "")
      . "\n";
    unless (ask_yes_no("Is it OK")) {
        exit(0);
    }

    foreach my $filename (
        'setup.py',
       ) {
        my @array;
        tie @array, 'Tie::File', $filename
          or die "Can't read $filename: $!\n";
        foreach (@array) {
            s/(version\s*=\s*')\d+\.\d+(\.\d+)?/$1$version/;
        }
    }

    unless( $what eq 'rebuild' ) {
        system("hg commit -m 'version patch $version'") and die $!;
        system("hg tag $version") and die $!;
    }
}
else {
    $version = 'devel';
}

#################################################################
# Sprzątanie
#################################################################

rmtree('build');

#################################################################
# Uruchomienie setupu
#################################################################

system("python setup.py bdist_egg") and die "Setup failed!";

#################################################################
# Kopiowanie
#################################################################

my $EGG_NAME = $MODULE_NAME . "-" . $version . "-" . $PYTHON_VERSION . ".egg";
my $EGG_FILE = catfile($FindBin::Bin, "dist", $EGG_NAME);

print "Uploading $EGG_NAME\n";
unless (ask_yes_no("Is it OK")) {
    exit(0);
}

unless( -f $EGG_FILE ) {
    die "$EGG_FILE not found. Setup failed?\n";
}

system("scp $EGG_FILE linode.mekk.waw.pl:www_download/python/");

print "Uploaded http://mekk.waw.pl/download/python/$EGG_NAME\n";

