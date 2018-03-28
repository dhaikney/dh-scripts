#!/usr/bin/perl
 
my $LINE_BEGIN="<w:p w:rsidR=\"000D1C42\" w:rsidRDefault=\"000D1C42\">";
my $LINE_END="</w:p>\n";
my $ITALICS="<w:i/>";
my $BOLD="<w:b/>";
my $POST_BOLD="<w:r><w:t>";
my $TEXT_BEGIN="<w:t xml:space=\"preserve\">";
my $TEXT_END="</w:t></w:r>";
my $RUN_BEGIN="<w:r>";
my $RUNSTYLE_BEGIN="<w:rPr>";
my $RUNSTYLE_END="</w:rPr>";
my $PARASTYLE_BEGIN="<w:pPr>";
my $PARASTYLE_END="</w:pPr>";


my $HEADER_ROW=0;

my $BOLD_ON=0;
my $ITALICS_ON=0;

sub openText(){
	

	print $RUN_BEGIN;
	if ($BOLD_ON or $ITALICS_ON)
	{
		print $RUNSTYLE_BEGIN; 
		print $ITALICS if ($ITALICS_ON);
		print $BOLD if ($BOLD_ON);
		print $RUNSTYLE_END;
	}
	print $TEXT_BEGIN;
}

sub closeText(){
	print $TEXT_END;
}


open (FILE, '/tmp/testfile.txt') or die "couldn't find file\n";
while ($line=<FILE>) {
chomp $line;

	print $LINE_BEGIN; 

	
if ($line =~ s/^=====(.*?)=====$/$1/){
	$HEADER_ROW=4;
 }
elsif ($line =~ s/^====(.*?)====$/$1/){
	$HEADER_ROW=3;
 }
elsif ($line =~ s/^===(.*?)===$/$1/){
	$HEADER_ROW=2;
 }
elsif ($line =~ s/^==(.*?)==$/$1/){
	$HEADER_ROW=1;
 }
elsif ($line =~ s/^=(.*?)=$/$1/){
	$HEADER_ROW=1;
 }

	if ($HEADER_ROW){
		print $PARASTYLE_BEGIN;
		print "<w:pStyle w:val=\"Heading" . $HEADER_ROW . "\"/>";
		print $PARASTYLE_END;
	}
	
	print $RUN_BEGIN . $TEXT_BEGIN;
	
if ($line=~/^\*\*(.*?)$/){
print ">>>>****BULLET**** $1\n";
 }
elsif ($line=~/^\*(.*?)$/){
print "****BULLET**** $1\n";
 }
elsif ($line=~/^\#\*\*(.*?)$/){
print "HASH** $1\n";
 }
elsif ($line=~/^\#\*(.*?)$/){
print "HASH* $1\n";
 }
elsif ($line=~/^\#(.*?)$/){
print "HASH $1\n";
 }

for  (my $key = 0; $key < length($line); $key++) {
if (substr ($line, $key, 3) eq "'''")
{
	$key += 3;
	$BOLD_ON = !$BOLD_ON;
	closeText();
	openText();

}

elsif (substr ($line, $key, 2) eq "''")
{
	$key += 2;
	$ITALICS_ON = !$ITALICS_ON;
	closeText();
	openText();
}


print substr ($line, $key, 1);
}


while ($line =~ /([^'])'{3}(.*?)'{3}([^'])/g){
	#print "Found BOLD $1\n";
 }
while ($line=~ /[^']'{2}([^']*?)'{2}[^']/g){
#print "Found ITALICS $1\n";

 }

	print $TEXT_END . $LINE_END;

	die "BOLD IS still ON" if ($BOLD_ON);
	die "ITALICS IS still ON" if ($ITALICS_ON);
	$HEADER_ROW=0;
}

 close (FILE);
 exit;
