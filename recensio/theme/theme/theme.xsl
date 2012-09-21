<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:dv="http://openplans.org/deliverance" xmlns:exsl="http://exslt.org/common" xmlns:xhtml="http://www.w3.org/1999/xhtml" version="1.0" exclude-result-prefixes="exsl dv xhtml">
  <xsl:output method="xml" indent="no" omit-xml-declaration="yes" media-type="text/html" encoding="utf-8" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>

    <xsl:template match="/">

        <!-- Pass incoming content through initial-stage filter. -->
        <xsl:variable name="initial-stage-rtf">
            <xsl:apply-templates select="/" mode="initial-stage"/>
        </xsl:variable>
        <xsl:variable name="initial-stage" select="exsl:node-set($initial-stage-rtf)"/>

        <!-- Now apply the theme to the initial-stage content -->
        <xsl:variable name="themedcontent-rtf">
            <xsl:apply-templates select="$initial-stage" mode="apply-theme"/>
        </xsl:variable>
        <xsl:variable name="content" select="exsl:node-set($themedcontent-rtf)"/>

        <!-- We're done, so generate some output by passing
            through a final stage. -->
        <xsl:apply-templates select="$content" mode="final-stage"/>

    </xsl:template>

    <!--

        Utility templates
    -->

    <xsl:template match="node()|@*" mode="initial-stage">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*" mode="initial-stage"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="/" mode="apply-theme">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title>recensio.net</title><base/></head><body>

	<xsl:comment> &lt;div style="float:left;"&gt; </xsl:comment>
	<xsl:comment>   &lt;img src="imgs/social_facebook.png" /&gt;&amp;nbsp;&lt;img src="imgs/social_twitter.png" /&gt; </xsl:comment>
    <xsl:comment> &lt;/div&gt;            </xsl:comment>

    <div id="container">

	  <div id="header">
	    <div class="float_right">

          <p class="login_links" id="portal-personaltools"><a id="login" href="#"><strong>Anmelden</strong></a>
            ||
            <a id="register" href="#"><strong>Registrieren</strong></a></p>
		  <xsl:comment> TODO: eingeloggt als  </xsl:comment>
          <p id="logged_in">
            <a href="#" id="user-name">Lilian Landes</a>
            |
            <a href="#" class="einstellungen">Einstellungen <img src="imgs/arrow.png" alt=""/></a>
            |
            <a href="#" id="logout">ausloggen</a>
          </p>
		  <div id="suche"><h2><label for="search"/></h2><input type="text" id="search" value="recensio.net durchsuchen"/><input type="button" value="suchen"/><br/><br/></div>
		  <p id="language">
		    Please choose your language:&#160;&#160;
		    <a href="#" class="language-de">Deutsch</a>&#160;|&#160;
		    <a href="#" class="language-fr">Fran&#231;ais</a>&#160;|&#160;
		    <a href="#" class="language-en">English</a>&#160;
		  </p>
	    </div>
	    <a href="/"><img src="++resource++recensio.theme.images/logo_recensio.png" alt="Recensio Logo" id="recensio_logo"/></a>
	  </div>

	  <div id="navigation">
        <div id="navi-left" class="bar-end"/>
	    <ul><li class="navFirst_element"><a href="#">Rezensionen</a></li>
		  <li><a href="#">Pr&#228;sentationen</a></li>
		  <li><a href="#">Themenbrwosing</a></li>
		  <li><a href="#">Autoren</a></li>
		  <li><a href="#">mitmachen</a></li>
		  <li class="navLast_element"><a href="#">Presse</a></li>
	    </ul><div id="navi-right" class="bar-end"/>
	  </div>

	  <div class="clear"/>

	  <div id="loc">
	    Sie sind hier: Startseite &gt; Willkommen
	  </div>

		<object width="900" height="150" id="page_image">
        <param name="movie" value="/++resource++recensio.theme.images/main.swf"/><param name="wmode" value="opaque"/><embed src="/++resource++recensio.theme.images/main.swf" wmode="opaque" width="900" height="150"/></object>


      <div id="mainContent" class="rounded_STYLE rounded">
        <div class="tl"/>
        <div class="tr"/>
        <dl class="portalMessage info"><dt>Information</dt>
          <dd>Example Notification</dd>
        </dl><div id="column3">
          <span><xsl:comment> portlets go here </xsl:comment></span>
          <div class="box">
            <xsl:comment>p&gt;&lt;i&gt;recensio.net steht unter der Leitung von Prof. Dr. Gudrun Gersmann, Direktorin des Deutschen Historischen Instituts Paris&lt;/i&gt;&lt;/p</xsl:comment>
          </div>
        </div>

        <div id="content">
          <xsl:comment> start content here </xsl:comment>
          <span id="error_fallback">
            We are sorry, there has been an error.
          </span>
        </div>

        <div id="viewlet-below-content"/>

        <div id="clear-after-viewlets" class="clear"/>
        <div class="bl"/>
        <div class="br"/>
      </div>

      <xsl:comment> &lt;div id="postit"&gt; </xsl:comment>
      <xsl:comment>   &lt;img src="imgs/postit_sm.png" width="148" height="102" border="0" alt="Newsletter / RSS-Feed" usemap="#postit" /&gt; </xsl:comment>
      <xsl:comment>   &lt;map name="postit"&gt; </xsl:comment>
      <xsl:comment>     &lt;area shape="poly" coords="13,23,114,11,117,37,16,55" </xsl:comment>
               <xsl:comment>           href="#" alt="Newsletter" title="Newsletter" /&gt; </xsl:comment>
               <xsl:comment>     &lt;area shape="poly" coords="20,91,122,70,113,39,11,58" </xsl:comment>
                        <xsl:comment>           href="#" alt="RSS-Feed" title="RSS-Feed" /&gt; </xsl:comment>
                        <xsl:comment>   &lt;/map&gt; </xsl:comment>
                        <xsl:comment> &lt;/div&gt; </xsl:comment>


	                    <div id="footer">

	                      <div class="column_footer">

		                    <div>
		                      <span><a href="http://www.dfg.de"><img src="imgs/logos/dfg_logo.png" alt="Logo der deutschen Forschungsgemeinschaft" class="logo"/></a>&#160; recensio.net ist ein von der Deutschen Forschungsgemeinschaft gef&#246;rdertes Gemeinschaftsprojekt folgender Instututionen</span><br/><a href="http://www.bsb-muenchen.de/"><img src="imgs/logos/bsb_logo.gif" alt="Logo der Bayerischen Staatsbibliothek"/></a>
		                      <a href="http://www.dhi-paris.fr/"><img src="imgs/logos/dhip_logo.png" alt="Logo des deutschen historischen Instituts Paris"/></a>
		                      <a href="http://www.ieg-mainz.de/likecms/index.php"><img src="imgs/logos/ieg_logo.gif" alt="Logo des Institus f&#xFC;r europ&#xE4;ische Geschichte"/></a>
	                        </div>

	                        <div id="notes">
		                      <a href="#">Impressum</a>
	                        </div>

	                      </div>

	                    </div>
	</div>


</body></html>
    </xsl:template>
    <xsl:template match="style|script|xhtml:style|xhtml:script" priority="5" mode="final-stage">
        <xsl:element name="{local-name()}" namespace="http://www.w3.org/1999/xhtml">
            <xsl:apply-templates select="@*" mode="final-stage"/>
            <xsl:value-of select="text()" disable-output-escaping="yes"/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="*" priority="3" mode="final-stage">
        <!-- Move elements without a namespace into
        the xhtml namespace. -->
        <xsl:choose>
            <xsl:when test="namespace-uri(.)">
                <xsl:copy>
                    <xsl:apply-templates select="@*|node()" mode="final-stage"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="{local-name()}" namespace="http://www.w3.org/1999/xhtml">
                    <xsl:apply-templates select="@*|node()" mode="final-stage"/>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <xsl:template match="node()|@*" priority="1" mode="final-stage">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*" mode="final-stage"/>
        </xsl:copy>
    </xsl:template>

    <!--

        Extra templates
    -->

</xsl:stylesheet>