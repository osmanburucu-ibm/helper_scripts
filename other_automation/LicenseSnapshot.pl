@rem= 'PERL for Windows -- A perl MUST be in search path
@echo off
@rem set LM_LICENSE_FILE=27016@cclic-mu
@rem set
@rem pause
perl %0 %1 %2 %3 %4 %5 %6 %7 %8 %9 

goto endofperl

@rem ';

##########################################################################
# On unix, put this as first line:
#!/usr/atria/bin/Perl
#
# Begin of Perl section

##########################################################################
# COMPANY:              IBM Deutschland GmbH - Rational Software
# PROJECT:              DarkLicense-Tool
# FUNCTION:             Displays number of licenses used
# KEYWORDS:
# AUTHOR:               diverent
#
# VERSION:              3.00J
##########################################################################
# History:
# 10.2014 		5.0   O.Buruc : changed ;)
# 09'2012		4.0	  H. Sternkicker : Added support for token licenses
# 03'2012       3.0J  J. Pross  
# 04.05.2004    2.0   D. Diebolt
# 21.02.2002    1.0   P. Imbach
#
##########################################################################
# Constants to be modified:
#
# Path where the log file is generated:
# On a Windows Client:
#my $logfilepath  = "C:\\tools\\";
# On a Unix Client:
my $logfilepath  = "/var/ibm/flexlm/log/";

# Tool to use for getting the atria license
# Windows:
my $clearlicense = "clearlicense ";
# Unix:
#my $clearlicense = "/usr/atria/bin/clearlicense";

# Tool to use for getting the FlexLM license
# Windows:
#my $lmstat	 = "c:\\IBMx86\\RationalRLKS\\common\\lmutil lmstat";
# Unix
#my $lmstat	 = "/opt/rational/flexlm/sun4_solaris2/lmstat";
my $lmstat	 = "/opt/IBM/RationalRLKS/bin/lmutil lmstat";

##########################################################################
# Supported Tools
my @Tools= ("ClearCase","ClearQuest","ClearQuestMultiSite","DOORS","TLSTOK");
my $arg;
my $licfilepath="";
require 5.000;
use strict;

#
# Argument pruefen und zerlegen
#--------------------------------
sub main
{
	my $argument = "";
	if ($#ARGV<0)
	{
		print"\n No Arguments!\n";
   		usage();
	}

	my $loop = "0";
	my $Tool2watch = "";
	my $ToolsFound = 0;
	# Altes Abarbeiten der übergebenen Argumente
	# foreach $arg(@ARGV) {
		# if ( lc($arg) eq "-h" ) { usage(); };
		# if ( lc($arg) eq "-i" ) { $loop = "1"; };
		# foreach my $Tool(@Tools) {
			# if ( substr($arg,1) eq $Tool) { 
				# $Tool2watch =  substr($arg,1);
				# $ToolsFound++; 
			# }
		# }
	# };
	# Neue Methode der Argumentbearbeitung
	$arg=shift(@ARGV);
	while ($arg) {
		if ( lc($arg) eq "-h" ) { usage(); };
		if ( lc($arg) eq "-i" ) { $loop = "1"; };
		if (lc($arg) eq "-f") { 
			$licfilepath ="-c ". shift(@ARGV); 
			print "$licfilepath\n";
		};
		
		foreach my $Tool(@Tools) {
	
			if ( substr($arg,1) eq $Tool) { 
				$Tool2watch =  substr($arg,1);
				$ToolsFound++; 
			}
		}
		$arg=shift(@ARGV);
	}
    
	if ($ToolsFound gt 1) {
		print "ERROR: Specified more than one Tool.\n";
		usage();
	};
	print "Running for Tool: $Tool2watch\n";

	$argument = $ARGV[0];
	if ($Tool2watch eq "ClearCase") { ClearCaseLicenseStats("ClearCase"); }
	if ($Tool2watch eq "MultiSite")	{ ClearCaseLicenseStats("MultiSite"); }

	do 	{
 		flexlmLicenseStats($Tool2watch);
		my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $time) = localtime();
    		printf(" Last run: %2.2d:%2.2d:%2.2d\n", $hour, $min, $sec);
		if (!$loop) { exit(0) };
		sleep(600);
	} while (1);
}

##########################################################################
# License Statistics for ClearCase Type of license
##########################################################################
sub ClearCaseLicenseStats 
   {
   my $toolLicense  = shift(@_);
   my @suchausgabe	= ();
   my @users		= ();
   my $maxliz		= 0;
   my $usedliz		= 0;
   my $freeliz		= 0;
   my $points		= "";
   my $sec			= "";
   my $min			= "";
   my $hour			= "";
   my $month		= "";
   my $year			= "";
   my $datum		= "";
   my $time			= "";
   my $logfile		= "";
   my $zeile		= "";
   my $day			= "";
   my $user			= "";
   my $muell		= "";
   my $i			= "";

   # Searching for the date and time, and fill the several variables
   #----------------------------------------------------------------

   ($sec, $min, $hour, $day , $month , $year) = (localtime)[0,1,2,3,4,5];
   $year=$year+1900;
   $month=$month+1;
   if ($sec<10) {$sec="0".$sec}
   if ($min<10) {$min="0".$min}
   if ($hour<10) {$hour="0".$hour}
   if ($day<10) {$day="0".$day}
   if ($month<10) {$month="0".$month}
   
   $datum=$year."_".$month."_".$day;
   $time=$hour.":".$min.":".$sec;
   
   # Creating the logfile name from the date
   #----------------------------------------
   #$logfile=$logfilepath.$year."_".$month."_".$toolLicense."_licenses.txt";
   $logfile=$logfilepath.$toolLicense."_licenses.txt";
   printf("\n Logfile used : $logfile \n");
   open (LOGFILE, ">>$logfile");

   # Read the licenses information
   #------------------------------
   @suchausgabe= `$clearlicense -product $toolLicense`;
   
   foreach $zeile (@suchausgabe){
      $user="";
      if ($zeile =~ m/Maximum active users/){
         ($muell, $maxliz) = split (/: /,$zeile);
         next;
      }
      if ($zeile =~ m/Current active users/){
         ($muell, $usedliz) = split (/: /,$zeile);
         next;
      }
      if ($zeile =~ m/Available licenses/){
         ($muell, $freeliz) = split (/: /,$zeile);
         next;
      }
      if ($zeile =~ m/(\W*)([\S]*)(.*minutes)/){
         push (@users, $2); 
         next;
      }
   }
   
   for ($i=1 ; $i <= $usedliz ; $i+=1) { $points=$points."\." }

#

# To be modified:
# The %-30s: that is the max number of license you've got
#   
printf LOGFILE "%-10s %-8s\|%-30s\|\tMaximum active users : %3d\tCurrent active users : %3d\tUnused licenses : %3d\tUsers : @users \n", 
$datum, $time, $points , $maxliz, $usedliz, $freeliz;

   close (LOGFILE);

}




##########################################################################
# License Statistics for flexlm Type of License
##########################################################################

sub flexlmLicenseStats 
{
   my $toolLicense	= shift(@_);
   my @suchausgabe	= ();
   my @users		= ();
   my $maxliz		= 0;
   my $usedliz		= 0;
   my $freeliz		= 0;
   my $points		= "";
   my $sec			= "";
   my $min			= "";
   my $hour			= "";
   my $month		= "";
   my $year			= "";
   my $datum		= "";
   my $time			= "";
   my $logfile		= "";
   my $zeile		= "";
   my $day			= "";
   my $user			= "";
   my $muell		= "";
   my $i			= "";
   my $lizenzname	= "";
   my $username		= "";
   my $userip		= "";
   my $userpc		= "";
   my $usedtool 	= "";
   my $users		= "";
   my $lizinuse		= "";
   my $tokenpercent	= "";
   my $tokenperuser	= "";
   my $therest 		= "";
   my $prodused 	= "";
   my $jazzused 	= "";
   my $jazztoken 	= "";
   my $jazzstartusage = "";
   my $ausgabewerte = "";
   my $startwochentag =  "";
   my $startdatum     = "";
	my $startzeit = "";
	my $anzliz = "";
	my $jazzlizanz = "";
   my $a1 = "";
   my $a2 = "";
   my $a3 = "";
   my $a4 = "";
   my $a5 = "";
   my $a6 = "";
   my $a7 = "";
   my $a8 = "";
   my $a9 = "";
   my $a10 = "";
   my $a11 = "";
   my $a12 = "";
   
   
   # Searching for the date and time, and fill the several variables
   #----------------------------------------------------------------

   ($sec, $min, $hour, $day , $month , $year) = (localtime)[0,1,2,3,4,5];
   $year=$year+1900;
   $month=$month+1;
   if ($sec<10) {$sec="0".$sec}
   if ($min<10) {$min="0".$min}
   if ($hour<10) {$hour="0".$hour}
   if ($day<10) {$day="0".$day}
   if ($month<10) {$month="0".$month}

   $datum=$year.".".$month.".".$day;
   $time=$hour.":".$min.":".$sec;

   # Creating the logfile name from the date
   #----------------------------------------
  # $logfile=$logfilepath.$year."_".$month."_".$toolLicense."_licenses.txt";
   $logfile=$logfilepath.$toolLicense."_licenses.txt";

   printf("\n Logfile used : $logfile \n");

   open (LOGFILE, ">>$logfile");

   # Read the licenses information
   #------------------------------
   # In meinen Tests musste ich zwingend immer den Pfad zur rational_server_perm.dat angeben
   if ($licfilepath ne "") {
		@suchausgabe= `$lmstat $licfilepath -a -f $toolLicense`;
	} else {
		@suchausgabe= `$lmstat -a -f $toolLicense`;
	
   }
   

   # Die ersten 12 Zeilen aus der Ausgabe löschen
   #----------------------------------------------
   for ($i=1 ; $i <= 12 ; $i+=1) { shift @suchausgabe; }
	# Untersuchen: nach  Token gesucht wird
	if ($toolLicense eq "TLSTOK") {
		$ausgabewerte = "";
		#printf ("SUCHAUSGABE=");
		#print "@suchausgabe";
		#printf ("===========================================\n");
		foreach $zeile (@suchausgabe){
			$zeile =~ s/^\s+//; # Entfernen der führenden Leerzeichen
			if ($zeile =~ /Users of $toolLicense/) { 
				($muell, $muell, $lizenzname, $muell, $muell, $muell, $maxliz, $muell, $muell, $muell, $muell,$muell , $lizinuse, $muell) = split ( /\s/ , $zeile);
				# last; # schleife verlassen wenn die Zeile mit den Tokens gefunden wurde
			}	elsif ($zeile =~ /start/) { 
				# jetzt sind wir in der entsprechenden ausgabezeile mit den verwendeten lizenzen
						#printf ("DieZeile=".$zeile);
						$jazzused = "";
						($username, $userip, $userpc, $prodused, $muell, $muell, $muell, $muell, $startwochentag, $startdatum, $startzeit, $anzliz, $therest) = split ( /\s/ , $zeile);
						$users=$users." $username";
						$usedliz=$usedliz+1;
						printf ($username." ".$userip." ".$userpc." | ".$prodused."-".$startwochentag."-".$startdatum."-".$startzeit."-".$anzliz." |||| ".$therest."\n");
						if (index($zeile, "JazzToken") != -1) {
							$prodused = "JazzToken";
							# Jazztokens used
							# a11 = Domäne
							($muell, $muell, $muell, $muell, $muell, $muell, $muell, $muell, $muell, $muell, $jazzused, $muell, $therest) = split ( /\#/ , $zeile);
							# printf ($username." ".$userpc." JAZZTOKEN ".$jazzused."-"."-TheRest:".$therest."\n");
							$therest =~ s/^\s+//; 
							#printf ("therest=".$therest."\n");
							($a1, $a2, $a3, $a4, $a5, $startdatum, $startzeit, $anzliz, $a8) = split ( /\s/, $therest);
							#printf ("AAAA=".$a1."|".$a2."|".$a3."|".$a4."|".$a5."||".$startdatum."|".$startzeit."|".$anzliz."|".$a8."|"."\n");
							($muell, $jazzstartusage, $jazztoken) = split ( /\,/ , $therest);
							chomp $jazzstartusage;
							chomp $jazztoken;
							($muell, $a2, $muell) = split ( /\s/ , $jazztoken);
							$jazztoken = $a2;
							#printf ($username." ".$userpc." JAZZTOKEN ".$jazzused."-".":".$jazzstartusage."|".$jazztoken."\n");
						}
						$ausgabewerte = $ausgabewerte.$datum." ".$time.",".$username.",".$userpc.",".$prodused.",".$jazzused.",".$startdatum.",".$startzeit.$anzliz ."\n" ;
						
			} else { 
				next;
			}
		}
		# Prozentzahl der verwendeten tokens berechnen
		$tokenpercent=0;
		if ($maxliz>0) {$tokenpercent=($lizinuse*100)/$maxliz};
		$tokenpercent=sprintf("%.0f",$tokenpercent);
		if ($usedliz>0) {$tokenperuser=($lizinuse)/$usedliz;}
		printf(" Active used tokens : $lizinuse \n");
		for ($i=1 ; $i <= $tokenpercent ; $i+=1) { $points=$points."\." }
		#
		# To be modified:
		# The %-100s: because we calculate the percentage of token licenses used
		#     
		#printf LOGFILE "%-10s %-8s\|%-100s\|\tTotal Licenses : %3d\tCurrent active used tokens : %3d\tTokens used per user : %3d\n", $datum, $time, $points , $maxliz, $lizinuse,$tokenperuser;
		printf LOGFILE $ausgabewerte;
		
	} else {
		# Normale floating Lizenzen auswerten
	   # Unnütze Zeilen raus filtern
	   #-----------------------------
	   foreach $zeile (@suchausgabe){
		chomp $zeile;
			if ($zeile =~ /Users of/) { 
				($muell, $muell, $lizenzname, $muell, $muell, $muell, $maxliz, $muell) = split ( /\s/ , $zeile);
			}
			if ($zeile =~ /\"$toolLicense\"/) { next }
			if ($zeile =~ /nodelocked/) { next }
			if ($zeile =~ /^$/) { next }  #^$ heisst, dass das Zeilenende auf den Zeilenanfang folgt  
			if ($zeile =~ /start/) {
				($muell, $muell, $muell, $muell, $username, $userip, $userpc, $muell) = split ( /\s/ , $zeile);
				$users=$users." $username";
				$usedliz=$usedliz+1;
			}
		}
		printf(" Active users : $usedliz \n"); 
		for ($i=1 ; $i <= $usedliz ; $i+=1) { $points=$points."\." }
		#
		# To be modified:
		# The %-30s: that is the max number of license you've got
		#     
		printf LOGFILE "%-10s %-8s\|%-30s\|\tTotal Licenses : %3d\tCurrent active users : %3d\tUsers : $users \n", $datum, $time, $points , $maxliz, $usedliz;
		printf " Users : $users \n";
	}



    close (LOGFILE);

}

##########################################################################
# HelpText
##########################################################################
sub usage 
{
	use File::Basename;

	print "\nDisplays the number of used licenses for one specific Rational Tool.\n\n";
	print "Usage: ".basename($0)." -<Tool>\n";
	print "\t-h \tDisplay Help\n";
	print "\t-i \tLoop forever\n";
	print "\t-f licfile \tcomplete path to rational_server_perm.dat\n\n";
	print "\tTools in:\n";

	foreach my $Tool (@Tools){
		printf "\t-%-20s Check the license usage for %s.\n", $Tool, $Tool;
	}
	die "\n";
}

main

# End of Perl section

__END__

:endofperl
