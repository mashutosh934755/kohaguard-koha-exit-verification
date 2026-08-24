#!/usr/bin/perl
use strict;
use warnings;

# Run inside the target Koha instance environment, e.g.:
# sudo koha-shell -c "perl /path/create-demo-data.pl --cardnumber DEMO001" yourinstance
#
# This is intentionally a TEST/DEMO utility. Do not run against production
# without reviewing local circulation rules, branches and item types.

use Getopt::Long qw(GetOptions);
use C4::Context;
use C4::Biblio qw(AddBiblio);
use C4::Circulation qw(AddIssue);
use MARC::Record;
use MARC::Field;
use Koha::Patrons;
use Koha::Libraries;
use Koha::ItemTypes;
use Koha::Items;
use Koha::Item;

my $cardnumber = '';
GetOptions('cardnumber=s' => \$cardnumber) or die "Bad arguments\n";
die "Usage: $0 --cardnumber DEMO_PATRON_CARD\n" unless $cardnumber;

my $patron = Koha::Patrons->find({ cardnumber => $cardnumber });
die "Patron not found\n" unless $patron;
my $library = Koha::Libraries->find($patron->branchcode) || Koha::Libraries->search()->next;
my $itemtype = Koha::ItemTypes->search()->next;
die "No library/item type available\n" unless $library && $itemtype;
my $branch = $library->branchcode;
my $itype = $itemtype->itemtype;

C4::Context->set_userenv(
    $patron->borrowernumber, $patron->userid, $patron->cardnumber,
    $patron->firstname, $patron->surname, $branch, $library->branchname,
    $patron->flags, $patron->email
);

my @books = (
 ['KGDEMO001','Artificial Intelligence in Academic Libraries','Demo Author One'],
 ['KGDEMO002','Digital Libraries and Knowledge Discovery','Demo Author Two'],
 ['KGDEMO003','Research Data Management in Universities','Demo Author Three'],
 ['KGDEMO004','Library Automation with Open Source Systems','Demo Author Four'],
 ['KGDEMO005','Scholarly Communication and Research Analytics','Demo Author Five'],
 ['KGDEMO006','Linked Data Applications in Libraries','Demo Author Six'],
 ['KGDEMO007','Institutional Repositories and Digital Preservation','Demo Author Seven'],
 ['KGDEMO008','Bibliometrics and Research Impact Assessment','Demo Author Eight'],
 ['KGDEMO009','Smart Library Technologies','Demo Author Nine'],
 ['KGDEMO010','Future of Academic Library Services','Demo Author Ten'],
);

for my $book (@books) {
    my ($barcode,$title,$author)=@$book;
    next if Koha::Items->search({barcode=>$barcode})->count;
    my $record=MARC::Record->new();
    $record->leader('00000nam a2200000 a 4500');
    $record->append_fields(
      MARC::Field->new('100','1',' ',a=>$author),
      MARC::Field->new('245','1','0',a=>$title),
      MARC::Field->new('260',' ',' ',b=>'KohaGuard Demo Publisher',c=>'2026'),
      MARC::Field->new('300',' ',' ',a=>'250 pages'),
      MARC::Field->new('942',' ',' ',c=>$itype),
    );
    my ($biblionumber,$biblioitemnumber)=AddBiblio($record,'',{disable_autolink=>1});
    die "Failed creating $barcode\n" unless $biblionumber;
    my $item=Koha::Item->new({
      biblionumber=>$biblionumber,
      biblioitemnumber=>$biblioitemnumber,
      barcode=>$barcode,
      homebranch=>$branch,
      holdingbranch=>$branch,
      itype=>$itype,
      itemcallnumber=>'KG-DEMO-'.substr($barcode,-3),
      notforloan=>0,itemlost=>0,withdrawn=>0,
    })->store;
    print "CREATED $barcode item=".$item->itemnumber."\n";
}

for my $n (1..5) {
    my $barcode=sprintf('KGDEMO%03d',$n);
    my $item=Koha::Items->search({barcode=>$barcode})->next or next;
    next if $item->checkout;
    my $issue=AddIssue($patron,$barcode);
    print $issue ? "ISSUED $barcode\n" : "FAILED $barcode\n";
}

print "Demo complete. KGDEMO001-005 should be issued; KGDEMO006-010 should remain not issued.\n";
