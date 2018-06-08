#!/usr/bin/env perl

use strict;
use warnings;
use diagnostics;

use Getopt::Std;
use Scalar::Util 'looks_like_number';
use List::Util 'shuffle';


sub show_help {
    print "\033[1m" . "Description:\n" . "\033[0m";
    print "  This scripts generate mazes using Kurskal algorithm.\n";
    print "\033[1m" . "\nUsage:\n" . "\033[0m";
    print "  $0 size without walls [OPTIONS]\n";
    print "  size must be greater than 1\n";
    print "\033[1m" . "\nOOptions:\n" . "\033[0m";
    print "\033[1m" . "  -h\n" . "\033[0m";
    print "    Shows this message\n";

    print "\n\n";

    exit;
}

sub show_incorrect_args {
    print "\033[1m\033[91m" . "Incorrect options\n" . "\033[0m";
    print "\033[91m" . "Showing help:\n\n" . "\033[0m";
    show_help();
}

if (scalar @ARGV < 1) {
    show_incorrect_args();
}

my $size = $ARGV[0];
if ($ARGV[0] ne '-h') {
    splice @ARGV, 0, 1;
}

my %options = ();
my $correct_options = getopts(":h", \%options);
if (!$correct_options) {
    show_incorrect_args();
}

if ($options{h}) {
    show_help();
}

if (!looks_like_number($size) || $size < 1) {
    show_incorrect_args();
}


sub printHash {
    my (%hash) = @_;

    print "{\n";
    foreach my $key (keys %hash) {
        print "\t$key => $hash{$key}\n"
    }
    print "}\n"
}
sub build_left_wall {
    my ($x, $y) = @_;

    my %new_wall = (
        x        => $x,
        y        => $y,
        leftSide => 1,
        topSide  => 0
    );

    return \%new_wall;
}
sub build_top_wall {
    my ($x, $y) = @_;

    my %new_wall = (
        x        => $x,
        y        => $y,
        leftSide => 0,
        topSide  => 1
    );

    return \%new_wall;
}
sub build_cell {
    my ($x, $y) = @_;

    my %new_cell = (
        x        => $x,
        y        => $y,
        leftSide => 1,
        topSide  => 1
    );

    return \%new_cell;
}
sub print_maze {
    my @cells = @{$_[0]};
    my @maze;
    for (my $y = 0; $y < (($size * 2) + 1); $y++) {
        for (my $x = 0; $x < (($size * 2) + 1); $x++) {
            $maze[$y][$x] = '#';
        }
    }
    foreach my $cell (@cells) {
        my $curr_x = ($cell->{x} * 2) + 1;
        my $curr_y = ($cell->{y} * 2) + 1;
        $maze[$curr_y][$curr_x] = ' ';
        if (!$cell->{leftSide}) {
            $maze[$curr_y][$curr_x - 1] = ' ';
        }
        if (!$cell->{topSide}) {
            $maze[$curr_y - 1][$curr_x] = ' ';
        }
    }

    foreach my $row (@maze) {
        foreach my $cell (@$row) {
            print "$cell";
        }
        print "\n";
    }
}

my @walls;
for (my $i = 0; $i < $size; $i++) {
    for (my $j = 0; $j < $size; $j++) {
        push  @walls, build_left_wall($j, $i) if ($j > 0);
        push  @walls, build_top_wall($j, $i) if ($i > 0);
    }
}
@walls = shuffle @walls;

my @cell_sets;
for (my $i = 0; $i < $size; $i++) {
    for (my $j = 0; $j < $size; $j++) {
        my @cell_set = (build_cell($i, $j));
        push  @cell_sets, \@cell_set;
    }
}

my $iter = 0;
foreach my $wall (@walls) {
    $iter++;
    my $curr_x = $wall->{x};
    my $curr_y = $wall->{y};
    my $other_x;
    my $other_y;
    if ($wall->{leftSide}) {
        $other_x = $curr_x - 1;
        $other_y = $curr_y;
    }
    else {
        $other_x = $curr_x;
        $other_y = $curr_y - 1;
    }

    my $curr_set_index = - 1;
    my $other_set_index = - 1;
    my $cell_set_index = 0;
    my $current_cell_ref;
    while ($cell_set_index < scalar @cell_sets) {
        my $cell_set = $cell_sets[$cell_set_index];
        foreach my $cell (@$cell_set) {
            if ($curr_x == $cell->{x} && $curr_y == $cell->{y}) {
                $curr_set_index = $cell_set_index;
                $current_cell_ref = \$cell;
                if ($other_set_index != - 1) {
                    last;
                }
            }
            if ($other_x == $cell->{x} && $other_y == $cell->{y}) {
                $other_set_index = $cell_set_index;
                if ($curr_set_index != - 1) {
                    last;
                }
            }
        }
        $cell_set_index++;
    }

    if ($curr_set_index != $other_set_index) {
        if ($wall->{leftSide}) {
            $$current_cell_ref->{leftSide} = 0;
        }
        if ($wall->{topSide}) {
            $$current_cell_ref->{topSide} = 0;
        }
        my $curr_set = $cell_sets[$curr_set_index];
        my $other_set = $cell_sets[$other_set_index];
        push @$curr_set, @$other_set;
        splice @cell_sets, $other_set_index, 1;
    }
}

print_maze($cell_sets[0]);