#!/usr/bin/perl
use v5.16;
use warnings;

use JSON::XS;
use MediaWiki::DumpFile::FastPages;

my $pages = MediaWiki::DumpFile::FastPages->new(\*STDIN);
while (my ($title, $text) = $pages->next) {
    print encode_json({ title => $title, text => $text }), "\n";
}
