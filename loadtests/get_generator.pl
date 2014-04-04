#/usr/bin/perl
my $req= "GET /igor/user/details?user=igor@igor.com HTTP/1.1\r\n".
  "User-Agent: YandexTank/1.1.1\r\n".
  "Host: localhost\r\n".
  "Accept-Encoding: gzip, deflate\r\n".
  "Connection: Close\r\n".
  "\r\n";
print length($req)."\n".$req;
