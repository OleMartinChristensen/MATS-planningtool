function [Argument] = ArgumentExtracter(line)
%ArgumentExtracter Extract the argument, surrounded by '<' and '>', from a string
%   The string represents a line from a XML file. The argument is converted
%   to a number aswell.


Argument = "";
ArgumentFound = false;
for x = 1:length(line)
    
        if(line(x) == '>')
            ArgumentFound = true;
        elseif( ArgumentFound == true )
            if( line(x) == '<' )
                ArgumentFound = false;
            else
                Argument = Argument + line(x);
            end
        end
end
Argument = str2num(Argument);

end

